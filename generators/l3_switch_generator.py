from pathlib import Path

from common_config_blocks import generar_bloque_ssh
from vlsm_from_config import calcular_vlsm_oficina


def buscar_transit_link_para_switch(config, switch_name, office_name):
    topology = config.get("topology", {})

    for link in topology.get("transit_links", []):
        if link.get("office") != office_name:
            continue

        if link.get("from_device") == switch_name:
            return {
                "interface": link["from_interface"],
                "ip": link["from_ip"],
                "neighbor_device": link["to_device"],
                "neighbor_ip": link["to_ip"],
                "network": link["network"].split("/")[0],
                "mask": link["mask"],
                "wildcard": link["wildcard"],
                "description": link.get(
                    "description",
                    f"ENLACE-{link['from_device']}-{link['to_device']}",
                ),
            }

        if link.get("to_device") == switch_name:
            return {
                "interface": link["to_interface"],
                "ip": link["to_ip"],
                "neighbor_device": link["from_device"],
                "neighbor_ip": link["from_ip"],
                "network": link["network"].split("/")[0],
                "mask": link["mask"],
                "wildcard": link["wildcard"],
                "description": link.get(
                    "description",
                    f"ENLACE-{link['to_device']}-{link['from_device']}",
                ),
            }

    return None


def generar_config_l3_switch(office, vlsm_plan, management_config, gateway_policy, config):
    switch_name = office.get("distribution_switch") or "SW-DIST"
        
    topology = config.get("topology", {})
    routing_defaults = topology.get("routing_defaults", {})
    ospf_process_id = routing_defaults.get("ospf_process_id", 1)
    ospf_area = routing_defaults.get("ospf_area", 0)

    transit_link = buscar_transit_link_para_switch(
        config=config,
        switch_name=switch_name,
        office_name=office["name"],
    )

    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {switch_name}")
    lineas.append("")

    if management_config.get("ssh", {}).get("enabled"):
        lineas.extend(generar_bloque_ssh(management_config.get("ssh", {})))

    lineas.append("! Habilitar routing capa 3")
    lineas.append("ip routing")
    lineas.append("")

    lineas.append("! Crear VLANs")
    for item in vlsm_plan:
        lineas.append(f"vlan {item['vlan_id']}")
        lineas.append(f" name {item['vlan_name']}")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! Interfaces VLAN / Gateways")
    for item in vlsm_plan:
        lineas.append(f"interface vlan {item['vlan_id']}")
        lineas.append(f" description GATEWAY-{item['vlan_name']}")
        lineas.append(f" ip address {item['gateway']} {item['mask']}")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

    if transit_link:
        lineas.append("! Enlace capa 3 hacia router de borde")
        lineas.append(f"interface {transit_link['interface']}")
        lineas.append(f" description ENLACE-HACIA-{transit_link['neighbor_device']}")
        lineas.append(" no switchport")
        lineas.append(f" ip address {transit_link['ip']} {transit_link['mask']}")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

        lineas.append("! Ruta por defecto hacia router de borde")
        lineas.append(f"ip route 0.0.0.0 0.0.0.0 {transit_link['neighbor_ip']}")
        lineas.append("")
    else:
        lineas.append("! Enlace capa 3 hacia router de borde pendiente de definir")
        lineas.append("! No se encontró transit_link en config['topology']['transit_links']")
        lineas.append("")

    lineas.append("! OSPF si aplica")

    if office["features"].get("ospf"):
        lineas.append("router ospf {}".format(ospf_process_id))
        lineas.append(" router-id 10.10.10.10")

        for item in vlsm_plan:
            lineas.append(
                f" network {item['network']} {item['wildcard']} area {ospf_area}"
            )

        if transit_link:
            lineas.append(
                f" network {transit_link['network']} {transit_link['wildcard']} area {ospf_area}"
            )

        lineas.append(" passive-interface default")

        if transit_link:
            lineas.append(f" no passive-interface {transit_link['interface']}")

        lineas.append("")

    else:
        lineas.append("! OSPF no habilitado para esta oficina")
        lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_l3_switches_desde_config(config, output_base_dir):
    gateway_policy = config["global"].get("gateway_policy", "last_usable")
    management_config = config.get("management", {})

    output_dir = Path(output_base_dir) / "configs" / "switches"
    output_dir.mkdir(parents=True, exist_ok=True)

    archivos_generados = []

    for office in config["offices"]:
        if office["inter_vlan_routing"] != "layer3_switch":
            continue

        vlsm_plan = calcular_vlsm_oficina(office, gateway_policy)

        config_text = generar_config_l3_switch(
            office=office,
            vlsm_plan=vlsm_plan,
            management_config=management_config,
            gateway_policy=gateway_policy,
            config=config,
            )
        switch_name = office.get("distribution_switch") or "SW-DIST"
        ruta = output_dir / f"{switch_name}.txt"
        ruta.write_text(config_text, encoding="utf-8")

        archivos_generados.append(ruta)

    return archivos_generados