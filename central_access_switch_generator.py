from pathlib import Path

from common_config_blocks import generar_bloque_ssh


OUTPUT_DIR = Path("outputs/central_access")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


SWITCHES_ACCESO = ["SW1", "SW2", "SW3"]

IPS_ADMIN_SWITCHES = {
    "SW1": "192.168.1.177",
    "SW2": "192.168.1.178",
    "SW3": "192.168.1.179",
}

MASCARA_ADMIN = "255.255.255.248"
GATEWAY_ADMIN = "192.168.1.182"

VLANS_CENTRAL = [
    {"id": 10, "nombre": "CPD"},
    {"id": 20, "nombre": "USUARIOS"},
    {"id": 30, "nombre": "IT"},
    {"id": 1, "nombre": "ADMINISTRACION"},
]

SYSLOG_SERVER_IP = "192.168.1.129"

VLAN_PERMITIDAS_TRUNK = "1,10,20,30"


def generar_config_switch_acceso(nombre_switch):
    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {nombre_switch}")
    lineas.append("")

    lineas.append("! Crear VLANs")
    for vlan in VLANS_CENTRAL:
        lineas.append(f"vlan {vlan['id']}")
        lineas.append(f" name {vlan['nombre']}")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! Configuracion Syslog")
    lineas.append(f"logging host {SYSLOG_SERVER_IP}")
    lineas.append("logging trap warnings")
    lineas.append("service timestamps log datetime msec")
    lineas.append("")

    lineas.extend(generar_bloque_ssh())

    lineas.append("! EtherChannel hacia SW-DIST")
    lineas.append("interface range fa0/23 - 24")
    lineas.append(" description ETHERCHANNEL-HACIA-SW-DIST")
    lineas.append(" switchport mode trunk")
    lineas.append(f" switchport trunk allowed vlan {VLAN_PERMITIDAS_TRUNK}")
    lineas.append(" channel-group 1 mode active")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("interface port-channel 1")
    lineas.append(" description TRUNK-ETHERCHANNEL-HACIA-SW-DIST")
    lineas.append(" switchport mode trunk")
    lineas.append(f" switchport trunk allowed vlan {VLAN_PERMITIDAS_TRUNK}")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("! Puertos de acceso VLAN 10 CPD")
    lineas.append("interface range fa0/1 - 8")
    lineas.append(" description ACCESO-VLAN10-CPD")
    lineas.append(" switchport mode access")
    lineas.append(" switchport access vlan 10")
    lineas.append(" spanning-tree portfast")
    lineas.append(" spanning-tree bpduguard enable")
    lineas.append(" switchport port-security")
    lineas.append(" switchport port-security maximum 2")
    lineas.append(" switchport port-security violation shutdown")
    lineas.append(" switchport port-security mac-address sticky")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("! Puertos de acceso VLAN 20 USUARIOS")
    lineas.append("interface range fa0/9 - 16")
    lineas.append(" description ACCESO-VLAN20-USUARIOS")
    lineas.append(" switchport mode access")
    lineas.append(" switchport access vlan 20")
    lineas.append(" spanning-tree portfast")
    lineas.append(" spanning-tree bpduguard enable")
    lineas.append(" switchport port-security")
    lineas.append(" switchport port-security maximum 2")
    lineas.append(" switchport port-security violation shutdown")
    lineas.append(" switchport port-security mac-address sticky")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("! Puertos de acceso VLAN 30 IT")
    lineas.append("interface range fa0/17 - 22")
    lineas.append(" description ACCESO-VLAN30-IT")
    lineas.append(" switchport mode access")
    lineas.append(" switchport access vlan 30")
    lineas.append(" spanning-tree portfast")
    lineas.append(" spanning-tree bpduguard enable")
    lineas.append(" switchport port-security")
    lineas.append(" switchport port-security maximum 2")
    lineas.append(" switchport port-security violation shutdown")
    lineas.append(" switchport port-security mac-address sticky")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("! SVI de administracion")
    lineas.append("interface vlan 1")
    lineas.append(" description ADMINISTRACION-SWITCH")
    lineas.append(f" ip address {IPS_ADMIN_SWITCHES[nombre_switch]} {MASCARA_ADMIN}")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("! Gateway de administracion")
    lineas.append(f"ip default-gateway {GATEWAY_ADMIN}")
    lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_resumen():
    lineas = []

    lineas.append("=== NETFORGE: SWITCHES DE ACCESO OFICINA CENTRAL ===")
    lineas.append("")
    lineas.append("Switches generados:")
    for switch in SWITCHES_ACCESO:
        lineas.append(f"- {switch}")
    lineas.append("")

    lineas.append("VLANs:")
    for vlan in VLANS_CENTRAL:
        lineas.append(f"- VLAN {vlan['id']}: {vlan['nombre']}")
    lineas.append("")

    lineas.append("Distribucion de puertos:")
    lineas.append("- Fa0/1 - Fa0/8: VLAN 10 CPD")
    lineas.append("- Fa0/9 - Fa0/16: VLAN 20 USUARIOS")
    lineas.append("- Fa0/17 - Fa0/22: VLAN 30 IT")
    lineas.append("- Fa0/23 - Fa0/24: EtherChannel trunk hacia SW-DIST")
    lineas.append("")

    lineas.append("Seguridad:")
    lineas.append("- Port-security habilitado en puertos de acceso")
    lineas.append("- Maximo 2 MAC por puerto")
    lineas.append("- Violacion: shutdown")
    lineas.append("- MAC sticky habilitado")
    lineas.append("- PortFast y BPDU Guard en puertos de acceso")
    lineas.append("")

    lineas.append("Syslog:")
    lineas.append(f"- Servidor Syslog: {SYSLOG_SERVER_IP}")
    lineas.append("")

    lineas.append("Administracion:")
    for switch in SWITCHES_ACCESO:
        lineas.append(f"- {switch}: {IPS_ADMIN_SWITCHES[switch]} {MASCARA_ADMIN}")
    lineas.append(f"- Gateway: {GATEWAY_ADMIN}")
    lineas.append("")

    return "\n".join(lineas)


def generar_switches_acceso():
    for switch in SWITCHES_ACCESO:
        config = generar_config_switch_acceso(switch)

        ruta = OUTPUT_DIR / f"{switch}.txt"
        ruta.write_text(config, encoding="utf-8")

        print(f"Config generada: {ruta}")

    resumen = generar_resumen()
    ruta_resumen = OUTPUT_DIR / "RESUMEN_SWITCHES_ACCESO.txt"
    ruta_resumen.write_text(resumen, encoding="utf-8")

    print(f"Resumen generado: {ruta_resumen}")


def main():
    generar_switches_acceso()
    print("\nGeneracion switches de acceso central completada.")


if __name__ == "__main__":
    main()