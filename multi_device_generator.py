from pathlib import Path
from graphviz import Digraph
import re

prompt = input("Describe la red: ").lower()

usa_nat = "nat" in prompt
usa_ospf = "ospf" in prompt
usa_dhcp = "dhcp" in prompt
usa_isp = "isp" in prompt or "internet" in prompt

BASE_OUTPUT_DIR = Path("outputs")
BASE_OUTPUT_DIR.mkdir(exist_ok=True)


def crear_carpeta_lab():
    numero = 1

    while True:
        carpeta = BASE_OUTPUT_DIR / f"lab_{numero:03d}"

        if not carpeta.exists():
            carpeta.mkdir()
            return carpeta

        numero += 1


OUTPUT_DIR = crear_carpeta_lab()

vlan_templates = [
    {
        "id": 10,
        "nombre": "ADMINISTRACION",
        "red": "192.168.10.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.10.1",
        "puerto": "f0/1",
        "descripcion": "PC-ADMINISTRACION",
    },
    {
        "id": 20,
        "nombre": "VENTAS",
        "red": "192.168.20.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.20.1",
        "puerto": "f0/2",
        "descripcion": "PC-VENTAS",
    },
    {
        "id": 30,
        "nombre": "SERVIDORES",
        "red": "192.168.30.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.30.1",
        "puerto": "f0/3",
        "descripcion": "SERVIDOR",
    },
    {
        "id": 40,
        "nombre": "INVITADOS",
        "red": "192.168.40.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.40.1",
        "puerto": "f0/4",
        "descripcion": "PC-INVITADOS",
    },
]


def detectar_cantidad_vlans(texto):
    coincidencia = re.search(r"(\d+)\s*vlans?", texto)

    if coincidencia:
        cantidad = int(coincidencia.group(1))
        return max(1, min(cantidad, len(vlan_templates)))

    if "vlan" in texto:
        return len(vlan_templates)

    return 1


def detectar_departamentos(texto):
    patrones = [
        r"vlans?:\s*([a-záéíóúñü,\s y]+)",
        r"departamentos?:\s*([a-záéíóúñü,\s y]+)",
        r"areas?:\s*([a-záéíóúñü,\s y]+)",
    ]

    for patron in patrones:
        coincidencia = re.search(patron, texto)

        if coincidencia:
            lista_texto = coincidencia.group(1)

            for palabra_corte in ["dhcp", "nat", "ospf", "isp", "internet"]:
                lista_texto = lista_texto.split(palabra_corte)[0]

            lista_texto = lista_texto.replace(" y ", ",")

            nombres = [nombre.strip().upper() for nombre in lista_texto.split(",")]
            nombres = [nombre for nombre in nombres if nombre]

            return nombres

    return []


cantidad_vlans = detectar_cantidad_vlans(prompt)
departamentos_detectados = detectar_departamentos(prompt)

vlans = {}

for indice, template in enumerate(vlan_templates[:cantidad_vlans]):
    vlan_id = template["id"]

    nombre_vlan = template["nombre"]

    if indice < len(departamentos_detectados):
        nombre_vlan = departamentos_detectados[indice]

    vlans[vlan_id] = {
        "nombre": nombre_vlan,
        "red": template["red"],
        "mascara": template["mascara"],
        "gateway": template["gateway"],
        "puerto": template["puerto"],
        "descripcion": f"PC-{nombre_vlan}",
    }


def guardar_config(nombre_archivo, lineas):
    ruta = OUTPUT_DIR / nombre_archivo
    contenido = "\n".join(lineas)
    ruta.write_text(contenido, encoding="utf-8")
    print(f"Config guardada: {ruta}")

def generar_diagrama():
    red = Digraph("NetForge")
    red.attr(rankdir="LR")

    red.node("SW1", "SW1-CORE")
    red.node("R1", "R1-CORE")

    # Nodos de VLAN dinámicos
    for vlan_id, datos in vlans.items():
        nodo_id = f"VLAN{vlan_id}"
        etiqueta = f"{datos['descripcion']}\nVLAN {vlan_id}"
        red.node(nodo_id, etiqueta)
        red.edge(nodo_id, "SW1", label=datos["puerto"].upper())

    # Trunk hacia router
    red.edge("SW1", "R1", label="Gi0/1 trunk")

    # ISP opcional
    if usa_isp:
        red.node("ISP", "R-ISP")
        red.edge("R1", "ISP", label="Gi0/0\n10.0.0.0/30")

    ruta_salida = OUTPUT_DIR / "topologia"
    red.render(str(ruta_salida), format="png", cleanup=True)

    print(f"Diagrama guardado: {OUTPUT_DIR / 'topologia.png'}")

# =========================
# SW1-CORE
# =========================

sw1 = []

sw1.append("enable")
sw1.append("configure terminal")
sw1.append("hostname SW1-CORE\n")

sw1.append("! Crear VLANs")
for vlan_id, datos in vlans.items():
    sw1.append(f"vlan {vlan_id}")
    sw1.append(f" name {datos['nombre']}")
sw1.append("")

sw1.append("! Puerto trunk hacia R1")
sw1.append("interface g0/1")
sw1.append(" description TRUNK-HACIA-R1-CORE")
sw1.append(" switchport mode trunk")
vlans_permitidas = ",".join(str(vlan_id) for vlan_id in vlans.keys())
sw1.append(f" switchport trunk allowed vlan {vlans_permitidas}")
sw1.append(" no shutdown")
sw1.append("exit\n")

sw1.append("! Puertos access")
for vlan_id, datos in vlans.items():
    sw1.append(f"interface {datos['puerto']}")
    sw1.append(f" description {datos['descripcion']}")
    sw1.append(" switchport mode access")
    sw1.append(f" switchport access vlan {vlan_id}")
    sw1.append(" spanning-tree portfast")
    sw1.append("exit\n")

sw1.append("end")
sw1.append("write memory")

guardar_config("SW1-CORE.txt", sw1)


# =========================
# R1-CORE
# =========================

r1 = []

r1.append("enable")
r1.append("configure terminal")
r1.append("hostname R1-CORE\n")

r1.append("! Interfaz física hacia switch")
r1.append("interface g0/1")
r1.append(" description TRUNK-HACIA-SW1-CORE")
r1.append(" no shutdown")
r1.append("exit\n")

r1.append("! Subinterfaces Router-on-a-Stick")
for vlan_id, datos in vlans.items():
    r1.append(f"interface g0/1.{vlan_id}")
    r1.append(f" description GATEWAY-{datos['nombre']}")
    r1.append(f" encapsulation dot1Q {vlan_id}")
    r1.append(f" ip address {datos['gateway']} {datos['mascara']}")
    if usa_nat:
        r1.append(" ip nat inside")
    r1.append("exit\n")

if usa_dhcp:
    r1.append("! Excluir gateways del DHCP")
    for datos in vlans.values():
        gateway = datos["gateway"]
        base = gateway.rsplit(".", 1)[0]
        r1.append(f"ip dhcp excluded-address {base}.1 {base}.20")
    r1.append("")

    r1.append("! DHCP Pools")
    for datos in vlans.values():
        r1.append(f"ip dhcp pool {datos['nombre']}")
        r1.append(f" network {datos['red']} {datos['mascara']}")
        r1.append(f" default-router {datos['gateway']}")
        r1.append(" dns-server 8.8.8.8")
        r1.append("")

if usa_isp or usa_nat:
    r1.append("! Enlace hacia ISP / Internet")
    r1.append("interface g0/0")
    r1.append(" description HACIA-ISP")
    r1.append(" ip address 10.0.0.1 255.255.255.252")
    if usa_nat:
        r1.append(" ip nat outside")
    r1.append(" no shutdown")
    r1.append("exit\n")

    r1.append("! Ruta por defecto hacia ISP")
    r1.append("ip route 0.0.0.0 0.0.0.0 10.0.0.2\n")

if usa_nat:
    r1.append("! NAT Overload")
    r1.append("access-list 1 permit 192.168.0.0 0.0.255.255")
    r1.append("ip nat inside source list 1 interface g0/0 overload\n")

if usa_ospf:
    r1.append("! OSPF")
    r1.append("router ospf 1")
    r1.append(" router-id 1.1.1.1")
    r1.append(" network 192.168.0.0 0.0.255.255 area 0")
    r1.append(" network 10.0.0.0 0.0.0.3 area 0")

    for vlan_id in vlans.keys():
        r1.append(f" passive-interface g0/1.{vlan_id}")

    r1.append(" no passive-interface g0/0")
    r1.append("")

r1.append("end")
r1.append("write memory")

guardar_config("R1-CORE.txt", r1)


# =========================
# R-ISP
# =========================

if usa_isp:
    isp = []

    isp.append("enable")
    isp.append("configure terminal")
    isp.append("hostname R-ISP\n")

    isp.append("interface g0/0")
    isp.append(" description HACIA-R1-CORE")
    isp.append(" ip address 10.0.0.2 255.255.255.252")
    isp.append(" no shutdown")
    isp.append("exit\n")

    isp.append("! Ruta de retorno hacia redes internas")
    isp.append("ip route 192.168.0.0 255.255.0.0 10.0.0.1\n")

    if usa_ospf:
        isp.append("! OSPF en ISP")
        isp.append("router ospf 1")
        isp.append(" router-id 3.3.3.3")
        isp.append(" network 10.0.0.0 0.0.0.3 area 0")
        isp.append("")

    isp.append("end")
    isp.append("write memory")

    guardar_config("R-ISP.txt", isp)


# =========================
# GUÍA DE PRUEBAS
# =========================

guia = []

guia.append("=== NETFORGE: GUÍA DE PRUEBAS ===\n")

guia.append("Topología recomendada:")
guia.append("PC1 Fa0 -> SW1 Fa0/1")
guia.append("SW1 Gi0/1 -> R1 Gi0/1")
guia.append("R1 Gi0/0 -> R-ISP Gi0/0\n")

guia.append("Orden de configuración:")
guia.append("1. Pegar outputs/SW1-CORE.txt en el switch")
guia.append("2. Pegar outputs/R1-CORE.txt en el router principal")
if usa_isp:
    guia.append("3. Pegar outputs/R-ISP.txt en el router ISP")
guia.append("")

guia.append("Pruebas en SW1:")
guia.append("show vlan brief")
guia.append("show interfaces trunk\n")

guia.append("Pruebas en R1:")
guia.append("show ip interface brief")
guia.append("show ip dhcp binding")
guia.append("show ip route")
if usa_nat:
    guia.append("show ip nat translations")
if usa_ospf:
    guia.append("show ip ospf neighbor")
guia.append("")

guia.append("Pruebas en PC1:")
guia.append("1. Desktop -> IP Configuration -> DHCP")
guia.append("2. ping 192.168.10.1")
if usa_isp:
    guia.append("3. ping 10.0.0.2")

guardar_config("GUIA_PRUEBAS.txt", guia)

generar_diagrama()

# =========================
# RESUMEN DEL LAB
# =========================

resumen = []

resumen.append("=== NETFORGE: RESUMEN DEL LAB ===\n")

resumen.append("Enunciado original:")
resumen.append(prompt)
resumen.append("")

resumen.append("Servicios detectados:")
if usa_dhcp:
    resumen.append("- DHCP")
if usa_nat:
    resumen.append("- NAT")
if usa_ospf:
    resumen.append("- OSPF")
if usa_isp:
    resumen.append("- ISP / Internet")
if not any([usa_dhcp, usa_nat, usa_ospf, usa_isp]):
    resumen.append("- Ninguno")

resumen.append("")

resumen.append("Dispositivos generados:")
resumen.append("- SW1-CORE")
resumen.append("- R1-CORE")
if usa_isp:
    resumen.append("- R-ISP")

resumen.append("")

resumen.append("VLANs generadas:")
for vlan_id, datos in vlans.items():
    resumen.append(f"- VLAN {vlan_id}: {datos['nombre']} | Red: {datos['red']}/24 | Gateway: {datos['gateway']} | Puerto: {datos['puerto']}")

resumen.append("")

resumen.append("Topología recomendada:")
resumen.append("PC1 Fa0 -> SW1 Fa0/1")
resumen.append("SW1 Gi0/1 -> R1 Gi0/1")
if usa_isp:
    resumen.append("R1 Gi0/0 -> R-ISP Gi0/0")

resumen.append("")

resumen.append("Archivos generados:")
resumen.append("- SW1-CORE.txt")
resumen.append("- R1-CORE.txt")
if usa_isp:
    resumen.append("- R-ISP.txt")
resumen.append("- GUIA_PRUEBAS.txt")
resumen.append("- RESUMEN_LAB.txt")

resumen.append("")

resumen.append("Pruebas clave:")
resumen.append("- Verificar VLANs en SW1 con: show vlan brief")
resumen.append("- Verificar trunk en SW1 con: show interfaces trunk")
resumen.append("- Verificar interfaces en R1 con: show ip interface brief")
if usa_dhcp:
    resumen.append("- Verificar DHCP en R1 con: show ip dhcp binding")
if usa_nat:
    resumen.append("- Verificar NAT en R1 con: show ip nat translations")
if usa_ospf:
    resumen.append("- Verificar OSPF con: show ip ospf neighbor")
if usa_isp:
    resumen.append("- Hacer ping desde PC1 hacia 10.0.0.2")

guardar_config("RESUMEN_LAB.txt", resumen)

print("\nGeneración completada.")