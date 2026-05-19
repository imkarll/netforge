from pathlib import Path

from common_config_blocks import generar_bloque_ssh
from vlsm_from_config import calcular_vlsm_oficina


def buscar_vlan_management(vlsm_plan):
    for item in vlsm_plan:
        if item["vlan_type"] == "management":
            return item

    return None


def obtener_ip_admin_switch(vlan_management, indice_switch):
    """
    Usa IPs desde el primer host de la VLAN de administración.
    Ejemplo:
    SW1 -> primer host
    SW2 -> primer host + 1
    """
    import ipaddress

    primera_ip = ipaddress.ip_address(vlan_management["first_host"])
    return str(primera_ip + indice_switch)


def generar_config_access_switch(
    switch_name,
    office,
    vlsm_plan,
    management_config,
    indice_switch,
):
    lineas = []

    switching = office["switching"]
    security = office["security"]
    port_security = security["port_security"]
    vlan_management = buscar_vlan_management(vlsm_plan)

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {switch_name}")
    lineas.append("")

    if management_config.get("ssh", {}).get("enabled"):
        lineas.extend(generar_bloque_ssh(management_config.get("ssh", {})))

    lineas.append("! Crear VLANs")
    for item in vlsm_plan:
        lineas.append(f"vlan {item['vlan_id']}")
        lineas.append(f" name {item['vlan_name']}")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! Trunk hacia switch de distribucion")
    lineas.append("interface fa0/24")
    lineas.append(f" description TRUNK-HACIA-{office.get('distribution_switch') or 'DISTRIBUCION'}")
    lineas.append(" switchport mode trunk")
    lineas.append(
        " switchport trunk allowed vlan "
        + ",".join(str(vlan) for vlan in switching["allowed_vlans"])
    )
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    vlans_no_management = [
        item for item in vlsm_plan if item["vlan_type"] != "management"
    ]

    if vlans_no_management:
        lineas.append("! Puertos de acceso repartidos por VLAN")

        puerto_inicio = 1
        puertos_por_vlan = 6

        for item in vlans_no_management:
            puerto_fin = puerto_inicio + puertos_por_vlan - 1

            lineas.append(f"interface range fa0/{puerto_inicio} - {puerto_fin}")
            lineas.append(f" description ACCESO-VLAN{item['vlan_id']}-{item['vlan_name']}")
            lineas.append(" switchport mode access")
            lineas.append(f" switchport access vlan {item['vlan_id']}")
            lineas.append(" spanning-tree portfast")
            lineas.append(" spanning-tree bpduguard enable")

            if port_security["enabled"]:
                lineas.append(" switchport port-security")
                lineas.append(f" switchport port-security maximum {port_security['max_mac']}")
                lineas.append(f" switchport port-security violation {port_security['violation']}")

                if port_security["sticky"]:
                    lineas.append(" switchport port-security mac-address sticky")

            lineas.append(" no shutdown")
            lineas.append("exit")
            lineas.append("")

            puerto_inicio = puerto_fin + 1

    if vlan_management:
        ip_admin = obtener_ip_admin_switch(vlan_management, indice_switch)

        lineas.append("! SVI de administracion")
        lineas.append(f"interface vlan {vlan_management['vlan_id']}")
        lineas.append(" description ADMINISTRACION-SWITCH")
        lineas.append(f" ip address {ip_admin} {vlan_management['mask']}")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

        lineas.append("! Gateway de administracion")
        lineas.append(f"ip default-gateway {vlan_management['gateway']}")
        lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_access_switches_desde_config(config, output_base_dir):
    gateway_policy = config["global"].get("gateway_policy", "last_usable")
    management_config = config.get("management", {})

    output_dir = Path(output_base_dir) / "configs" / "switches"
    output_dir.mkdir(parents=True, exist_ok=True)

    archivos_generados = []

    for office in config["offices"]:
        vlsm_plan = calcular_vlsm_oficina(office, gateway_policy)

        for indice, switch_name in enumerate(office["access_switches"], start=0):
            config_text = generar_config_access_switch(
                switch_name=switch_name,
                office=office,
                vlsm_plan=vlsm_plan,
                management_config=management_config,
                indice_switch=indice,
            )

            ruta = output_dir / f"{switch_name}.txt"
            ruta.write_text(config_text, encoding="utf-8")
            archivos_generados.append(ruta)

    return archivos_generados