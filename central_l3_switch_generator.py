from pathlib import Path

from vlsm_calculator import calcular_vlsm


OUTPUT_DIR = Path("outputs/central_l3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


VLANS_CENTRAL = [
    {"id": 20, "nombre": "USUARIOS", "hosts": 80},
    {"id": 10, "nombre": "CPD", "hosts": 20},
    {"id": 30, "nombre": "IT", "hosts": 10},
    {"id": 1, "nombre": "ADMINISTRACION", "hosts": 6},
]


def construir_necesidades_vlsm():
    necesidades = []

    for vlan in VLANS_CENTRAL:
        necesidades.append(
            {
                "nombre": f"VLAN {vlan['id']} {vlan['nombre']}",
                "hosts": vlan["hosts"],
            }
        )

    return necesidades


def asociar_vlans_con_vlsm(subredes):
    vlans_config = []

    for vlan, subred in zip(VLANS_CENTRAL, subredes):
        vlans_config.append(
            {
                "id": vlan["id"],
                "nombre": vlan["nombre"],
                "red": subred["red"],
                "prefijo": subred["prefijo"],
                "mascara": subred["mascara"],
                "wildcard": subred["wildcard"],
                "gateway": subred["gateway_recomendado"],
                "primer_host": subred["primer_host"],
                "ultimo_host": subred["ultimo_host"],
                "broadcast": subred["broadcast"],
                "hosts_utiles": subred["hosts_utiles"],
            }
        )

    return vlans_config


def generar_config_switch_l3(vlans_config):
    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append("hostname SW-DIST")
    lineas.append("")

    lineas.append("! Habilitar routing capa 3")
    lineas.append("ip routing")
    lineas.append("")

    lineas.append("! Crear VLANs")
    for vlan in vlans_config:
        lineas.append(f"vlan {vlan['id']}")
        lineas.append(f" name {vlan['nombre']}")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! Interfaces VLAN / Gateways")
    for vlan in vlans_config:
        lineas.append(f"interface vlan {vlan['id']}")
        lineas.append(f" description GATEWAY-{vlan['nombre']}")
        lineas.append(f" ip address {vlan['gateway']} {vlan['mascara']}")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! Enlace capa 3 hacia R1 pendiente de definir")
    lineas.append("! Ejemplo futuro:")
    lineas.append("! interface g0/1")
    lineas.append("!  no switchport")
    lineas.append("!  ip address <IP_SW_DIST_R1> <MASCARA>")
    lineas.append("!  no shutdown")
    lineas.append("")

    lineas.append("! Ruta por defecto hacia R1 pendiente de definir")
    lineas.append("! ip route 0.0.0.0 0.0.0.0 <IP_R1_LAN>")
    lineas.append("")

    lineas.append("! OSPF preparado para publicar VLANs de la oficina central")
    lineas.append("router ospf 1")
    lineas.append(" router-id 10.10.10.10")

    for vlan in vlans_config:
        lineas.append(f" network {vlan['red']} {vlan['wildcard']} area 0")

    lineas.append(" passive-interface default")
    lineas.append("! no passive-interface <INTERFAZ-HACIA-R1>")
    lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_resumen(vlans_config):
    lineas = []

    lineas.append("=== NETFORGE: OFICINA CENTRAL - SWITCH L3 ===")
    lineas.append("")

    for vlan in vlans_config:
        lineas.append(f"VLAN {vlan['id']} - {vlan['nombre']}")
        lineas.append(f"  Red: {vlan['red']}/{vlan['prefijo']}")
        lineas.append(f"  Máscara: {vlan['mascara']}")
        lineas.append(f"  Wildcard: {vlan['wildcard']}")
        lineas.append(f"  Gateway/SVI: {vlan['gateway']}")
        lineas.append(f"  Rango hosts: {vlan['primer_host']} - {vlan['ultimo_host']}")
        lineas.append(f"  Broadcast: {vlan['broadcast']}")
        lineas.append("")

    return "\n".join(lineas)


def generar_switch_l3_central():
    necesidades = construir_necesidades_vlsm()
    subredes = calcular_vlsm("192.168.1.0/24", necesidades)
    vlans_config = asociar_vlans_con_vlsm(subredes)

    config = generar_config_switch_l3(vlans_config)
    resumen = generar_resumen(vlans_config)

    ruta_config = OUTPUT_DIR / "SW-DIST.txt"
    ruta_resumen = OUTPUT_DIR / "RESUMEN_CENTRAL_L3.txt"

    ruta_config.write_text(config, encoding="utf-8")
    ruta_resumen.write_text(resumen, encoding="utf-8")

    print(f"Config generada: {ruta_config}")
    print(f"Resumen generado: {ruta_resumen}")


def main():
    generar_switch_l3_central()
    print("\nGeneración switch L3 central completada.")


if __name__ == "__main__":
    main()