from pathlib import Path
import re


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def normalizar_texto(texto):
    return texto.lower()


def detectar_redes(texto):
    patron = r"\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b"
    return re.findall(patron, texto)


def detectar_tecnologias(texto):
    tecnologias = {
        "OSPF": "ospf" in texto,
        "NAT/PAT": "nat" in texto or "pat" in texto,
        "GRE VPN": "gre" in texto or "vpn" in texto,
        "SSH": "ssh" in texto,
        "TFTP": "tftp" in texto,
        "Syslog": "syslog" in texto,
        "EtherChannel": "etherchannel" in texto,
        "STP": "stp" in texto,
        "Port Security": "seguridad de puerto" in texto or "port security" in texto,
        "VLSM": "vlsm" in texto or "subredes" in texto,
        "DHCP": "dhcp" in texto,
    }

    return [nombre for nombre, detectado in tecnologias.items() if detectado]


def expandir_rango(prefijo, inicio, fin):
    return [f"{prefijo}{numero}" for numero in range(inicio, fin + 1)]


def ordenar_dispositivos(lista):
    def clave(nombre):
        coincidencia = re.search(r"(\d+)", nombre)
        return int(coincidencia.group(1)) if coincidencia else 999

    return sorted(lista, key=clave)


def detectar_pcs_en_listas(texto_original):
    pcs = set()

    # Detecta frases tipo: PC 1, 3, y 5 / PC 7, 9 y 11
    coincidencias = re.findall(
        r"\bPCs?\s+((?:\d+\s*,?\s*(?:y\s*)?)+)",
        texto_original,
        re.IGNORECASE,
    )

    for grupo in coincidencias:
        numeros = re.findall(r"\d+", grupo)

        for numero in numeros:
            pcs.add(f"PC {numero}")

    return pcs


def detectar_dispositivos(texto_original):
    dispositivos = {}

    routers_internet = set(re.findall(r"\bI[1-6]\b", texto_original, re.IGNORECASE))
    routers_empresa = set(re.findall(r"\bR[1-2]\b", texto_original, re.IGNORECASE))
    switches = set(re.findall(r"\bSW\d+\b", texto_original, re.IGNORECASE))
    pcs = set(re.findall(r"\bPC\s?\d+\b", texto_original, re.IGNORECASE))

    # Detectar rangos simples tipo "I1-I6", "I1 hasta I6", "I1 a I6"
    rangos_i = re.findall(
        r"\bI(\d+)\b\s*(?:hasta|-|a)\s*\bI?(\d+)\b",
        texto_original,
        re.IGNORECASE,
    )

    for inicio, fin in rangos_i:
        routers_internet.update(expandir_rango("I", int(inicio), int(fin)))

    # Detectar rangos con texto intermedio:
    # "desde el I1 (Internet 1) hasta el I6"
    rangos_i_largos = re.findall(
        r"\bI(\d+)\b.{0,80}?\bhasta\b.{0,80}?\bI(\d+)\b",
        texto_original,
        re.IGNORECASE | re.DOTALL,
    )

    for inicio, fin in rangos_i_largos:
        routers_internet.update(expandir_rango("I", int(inicio), int(fin)))

    # Detectar rangos SW tipo "SW1-SW6", "SW1 hasta SW6"
    rangos_sw = re.findall(
        r"\bSW(\d+)\b\s*(?:hasta|-|a)\s*\bSW?(\d+)\b",
        texto_original,
        re.IGNORECASE,
    )

    for inicio, fin in rangos_sw:
        switches.update(expandir_rango("SW", int(inicio), int(fin)))

    # Si el enunciado habla de seis switches, inferimos SW1-SW6
    if "seis switches" in texto_original.lower() or "6 switches" in texto_original.lower():
        switches.update(expandir_rango("SW", 1, 6))

    # Detectar PCs en listas tipo "PC 1, 3 y 5"
    pcs.update(detectar_pcs_en_listas(texto_original))

    dispositivos["routers_internet"] = ordenar_dispositivos(routers_internet)
    dispositivos["routers_empresa"] = ordenar_dispositivos(routers_empresa)
    dispositivos["switches"] = ordenar_dispositivos(switches)
    dispositivos["pcs"] = ordenar_dispositivos(pcs)

    return dispositivos

def detectar_vlan_central(texto):
    vlans = []

    if "cpd" in texto:
        vlans.append({"id": 10, "nombre": "CPD", "hosts": 20})

    if "usuarios" in texto:
        vlans.append({"id": 20, "nombre": "Usuarios", "hosts": 80})

    if "it" in texto:
        vlans.append({"id": 30, "nombre": "IT", "hosts": 10})

    if "administración" in texto or "administracion" in texto:
        vlans.append({"id": 1, "nombre": "Administracion", "hosts": "extra"})

    return vlans


def detectar_vlan_remota(texto):
    vlans = []

    if "fábrica" in texto or "fabrica" in texto:
        vlans.append({"id": 10, "nombre": "Fabrica", "hosts": 20})

    if "distribución" in texto or "distribucion" in texto:
        vlans.append({"id": 20, "nombre": "Distribucion", "hosts": 20})

    if "administración" in texto or "administracion" in texto:
        vlans.append({"id": 1, "nombre": "Administracion", "hosts": "extra"})

    return vlans


def detectar_servicios_servidores(texto):
    servidores = []

    if "servidor web" in texto:
        servidores.append("Servidor Web")

    if "syslog" in texto:
        servidores.append("Servidor Syslog")

    if "tftp" in texto:
        servidores.append("Servidor TFTP")

    return servidores


def detectar_requisitos(texto_original):
    texto = normalizar_texto(texto_original)

    redes = detectar_redes(texto_original)
    tecnologias = detectar_tecnologias(texto)
    dispositivos = detectar_dispositivos(texto_original)

    requisitos = {
        "redes_detectadas": redes,
        "tecnologias": tecnologias,
        "dispositivos": dispositivos,
        "internet": {
            "detectado": "internet" in texto or "isp" in texto,
            "routers": dispositivos["routers_internet"],
            "red_base": "70.0.0.0/24" if "70.0.0.0/24" in texto else None,
            "routing": "OSPF" if "ospf" in texto else None,
            "enlaces_punto_a_punto": "punto a punto" in texto or "seriales" in texto,
        },
        "oficina_central": {
            "detectado": "oficina central" in texto,
            "red_base": "192.168.1.0/24" if "192.168.1.0/24" in texto else None,
            "vlans": detectar_vlan_central(texto),
            "switches_acceso": [sw for sw in dispositivos["switches"] if sw in ["SW1", "SW2", "SW3"]],
            "switch_l3": "switch de capa 3" in texto or "switch de distribución" in texto or "switch de distribucion" in texto,
            "features": [],
        },
        "oficina_remota": {
            "detectado": "oficina remota" in texto or "delegación remota" in texto or "delegacion remota" in texto,
            "red_base": "172.20.0.0/24" if "172.20.0.0/24" in texto else None,
            "vlans": detectar_vlan_remota(texto),
            "routing": "Router-on-a-stick" if "router-on-a-stick" in texto else None,
            "features": [],
        },
        "vpn": {
            "detectado": "vpn" in texto or "gre" in texto,
            "tipo": "GRE" if "gre" in texto else None,
            "red_base": "172.16.0.0/16" if "172.16.0.0/16" in texto else None,
            "routing": "OSPF" if "ospf" in texto else None,
        },
        "gestion": {
            "ssh": "ssh" in texto,
            "backup_tftp": "tftp" in texto,
            "guardar_nvram": "nvram" in texto or "write memory" in texto or "guardar" in texto,
        },
        "servidores": detectar_servicios_servidores(texto),
    }

    if "etherchannel" in texto:
        requisitos["oficina_central"]["features"].append("EtherChannel")

    if "seguridad de puerto" in texto or "port security" in texto:
        requisitos["oficina_central"]["features"].append("Port Security")

    if "syslog" in texto:
        requisitos["oficina_central"]["features"].append("Syslog")

    if "tftp" in texto:
        requisitos["oficina_central"]["features"].append("TFTP Backup")

    if "stp" in texto:
        requisitos["oficina_remota"]["features"].append("STP")

    if "troncales" in texto or "trunk" in texto:
        requisitos["oficina_remota"]["features"].append("Trunks")

    return requisitos


def generar_resumen(requisitos):
    lineas = []

    lineas.append("=== NETFORGE: REQUISITOS DETECTADOS ===\n")

    lineas.append("REDES DETECTADAS:")
    if requisitos["redes_detectadas"]:
        for red in requisitos["redes_detectadas"]:
            lineas.append(f"- {red}")
    else:
        lineas.append("- Ninguna")
    lineas.append("")

    lineas.append("TECNOLOGÍAS DETECTADAS:")
    if requisitos["tecnologias"]:
        for tecnologia in requisitos["tecnologias"]:
            lineas.append(f"- {tecnologia}")
    else:
        lineas.append("- Ninguna")
    lineas.append("")

    lineas.append("DISPOSITIVOS DETECTADOS:")
    for tipo, lista in requisitos["dispositivos"].items():
        lineas.append(f"- {tipo}: {', '.join(lista) if lista else 'Ninguno'}")
    lineas.append("")

    internet = requisitos["internet"]
    lineas.append("INTERNET / ISP:")
    lineas.append(f"- Detectado: {'sí' if internet['detectado'] else 'no'}")
    lineas.append(f"- Routers Internet: {', '.join(internet['routers']) if internet['routers'] else 'Ninguno'}")
    lineas.append(f"- Red base: {internet['red_base'] or 'No detectada'}")
    lineas.append(f"- Routing: {internet['routing'] or 'No detectado'}")
    lineas.append(f"- Enlaces punto a punto/seriales: {'sí' if internet['enlaces_punto_a_punto'] else 'no'}")
    lineas.append("")

    central = requisitos["oficina_central"]
    lineas.append("OFICINA CENTRAL:")
    lineas.append(f"- Detectada: {'sí' if central['detectado'] else 'no'}")
    lineas.append(f"- Red base: {central['red_base'] or 'No detectada'}")
    lineas.append("- VLANs:")
    if central["vlans"]:
        for vlan in central["vlans"]:
            lineas.append(f"  - VLAN {vlan['id']}: {vlan['nombre']} | Hosts: {vlan['hosts']}")
    else:
        lineas.append("  - Ninguna")
    lineas.append(f"- Switches de acceso: {', '.join(central['switches_acceso']) if central['switches_acceso'] else 'No detectados'}")
    lineas.append(f"- Switch capa 3/distribución: {'sí' if central['switch_l3'] else 'no'}")
    lineas.append(f"- Features: {', '.join(central['features']) if central['features'] else 'Ninguna'}")
    lineas.append("")

    remota = requisitos["oficina_remota"]
    lineas.append("OFICINA REMOTA:")
    lineas.append(f"- Detectada: {'sí' if remota['detectado'] else 'no'}")
    lineas.append(f"- Red base: {remota['red_base'] or 'No detectada'}")
    lineas.append("- VLANs:")
    if remota["vlans"]:
        for vlan in remota["vlans"]:
            lineas.append(f"  - VLAN {vlan['id']}: {vlan['nombre']} | Hosts: {vlan['hosts']}")
    else:
        lineas.append("  - Ninguna")
    lineas.append(f"- Routing: {remota['routing'] or 'No detectado'}")
    lineas.append(f"- Features: {', '.join(remota['features']) if remota['features'] else 'Ninguna'}")
    lineas.append("")

    vpn = requisitos["vpn"]
    lineas.append("VPN:")
    lineas.append(f"- Detectada: {'sí' if vpn['detectado'] else 'no'}")
    lineas.append(f"- Tipo: {vpn['tipo'] or 'No detectado'}")
    lineas.append(f"- Red base túnel: {vpn['red_base'] or 'No detectada'}")
    lineas.append(f"- Routing: {vpn['routing'] or 'No detectado'}")
    lineas.append("")

    gestion = requisitos["gestion"]
    lineas.append("GESTIÓN:")
    lineas.append(f"- SSH: {'sí' if gestion['ssh'] else 'no'}")
    lineas.append(f"- Backup TFTP: {'sí' if gestion['backup_tftp'] else 'no'}")
    lineas.append(f"- Guardar localmente/NVRAM: {'sí' if gestion['guardar_nvram'] else 'no'}")
    lineas.append("")

    lineas.append("SERVIDORES:")
    if requisitos["servidores"]:
        for servidor in requisitos["servidores"]:
            lineas.append(f"- {servidor}")
    else:
        lineas.append("- Ninguno")

    return "\n".join(lineas)


def main():
    print("Pega el enunciado completo. Cuando termines, escribe una línea con solo FIN:\n")

    lineas = []

    while True:
        linea = input()

        if linea.strip().upper() == "FIN":
            break

        lineas.append(linea)

    texto = "\n".join(lineas)

    requisitos = detectar_requisitos(texto)
    resumen = generar_resumen(requisitos)

    print("\n" + resumen)

    ruta = OUTPUT_DIR / "requisitos_detectados.txt"
    ruta.write_text(resumen, encoding="utf-8")

    print(f"\nResumen guardado en: {ruta}")


if __name__ == "__main__":
    main()