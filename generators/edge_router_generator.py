from pathlib import Path

from common_config_blocks import generar_bloque_ssh
from vlsm_from_config import calcular_vlsm_oficina


def buscar_conexion_edge_para_router(config, router_name):
    internet = config.get("internet", {})

    if not internet.get("enabled"):
        return None

    for conexion in internet.get("edge_connections", []):
        if conexion["enterprise_router"] == router_name:
            return conexion

    return None


def buscar_transit_link_para_router(config, router_name, office_name):
    topology = config.get("topology", {})

    for link in topology.get("transit_links", []):
        if link.get("office") != office_name:
            continue

        if link.get("from_device") == router_name:
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

        if link.get("to_device") == router_name:
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


def generar_acl_nat(vlsm_plan, acl_number):
    lineas = []

    lineas.append("! ACL para NAT/PAT de redes internas")

    for item in vlsm_plan:
        lineas.append(
            f"access-list {acl_number} permit {item['network']} {item['wildcard']}"
        )

    lineas.append("")
    return lineas


def generar_config_edge_router(router_name, office, vlsm_plan, config):
    lineas = []

    management_config = config.get("management", {})
    topology = config.get("topology", {})
    interface_defaults = topology.get("interface_defaults", {})
    routing_defaults = topology.get("routing_defaults", {})
    nat_defaults = topology.get("nat_defaults", {})

    edge_connection = buscar_conexion_edge_para_router(config, router_name)
    transit_link = buscar_transit_link_para_router(
        config=config,
        router_name=router_name,
        office_name=office["name"],
    )

    wan_interface = interface_defaults.get("edge_wan_interface", "g0/0")
    ospf_process_id = routing_defaults.get("ospf_process_id", 1)
    ospf_area = routing_defaults.get("ospf_area", 0)
    nat_acl_number = nat_defaults.get("acl_number", 1)

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {router_name}")
    lineas.append("")

    if management_config.get("ssh", {}).get("enabled"):
        lineas.extend(generar_bloque_ssh(management_config.get("ssh", {})))

    if edge_connection:
        lineas.append("! Interfaz hacia Internet / ISP")
        lineas.append(f"interface {wan_interface}")
        lineas.append(f" description ENLACE-HACIA-{edge_connection['internet_router']}")
        lineas.append(f" ip address {edge_connection['enterprise_ip']} 255.255.255.0")
        lineas.append(" ip nat outside")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

        lineas.append("! Ruta por defecto hacia Internet")
        lineas.append(f"ip route 0.0.0.0 0.0.0.0 {edge_connection['internet_ip']}")
        lineas.append("")
    else:
        lineas.append("! Enlace hacia Internet / ISP pendiente de definir")
        lineas.append(f"! interface {wan_interface}")
        lineas.append("!  description ENLACE-HACIA-ISP")
        lineas.append("!  ip address <IP_PUBLICA> <MASCARA>")
        lineas.append("!  ip nat outside")
        lineas.append("!  no shutdown")
        lineas.append("!")
        lineas.append("! Ruta por defecto pendiente")
        lineas.append("! ip route 0.0.0.0 0.0.0.0 <NEXT_HOP_ISP>")
        lineas.append("")

    if transit_link:
        lineas.append("! Enlace interno hacia LAN")
        lineas.append(f"interface {transit_link['interface']}")
        lineas.append(f" description ENLACE-HACIA-{transit_link['neighbor_device']}")
        lineas.append(f" ip address {transit_link['ip']} {transit_link['mask']}")
        lineas.append(" ip nat inside")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")
    else:
        lineas.append("! Enlace interno hacia LAN pendiente de definir")
        lineas.append("! No se encontró transit_link en config['topology']['transit_links']")
        lineas.append("! interface <INTERFAZ_LAN>")
        lineas.append("!  description ENLACE-HACIA-LAN")
        lineas.append("!  ip address <IP_TRANSITO_ROUTER> <MASCARA>")
        lineas.append("!  ip nat inside")
        lineas.append("!  no shutdown")
        lineas.append("")

    lineas.append("! Rutas hacia VLANs de la oficina")

    if transit_link:
        for item in vlsm_plan:
            lineas.append(
                f"ip route {item['network']} {item['mask']} {transit_link['neighbor_ip']}"
            )
    else:
        lineas.append("! Rutas pendientes: falta transit_link hacia LAN")
        for item in vlsm_plan:
            lineas.append(f"! ip route {item['network']} {item['mask']} <NEXT_HOP_LAN>")

    lineas.append("")

    if office["features"].get("nat"):
        lineas.extend(generar_acl_nat(vlsm_plan, nat_acl_number))

        if edge_connection:
            lineas.append("! NAT/PAT Overload")
            lineas.append(
                f"ip nat inside source list {nat_acl_number} interface {wan_interface} overload"
            )
            lineas.append("")
        else:
            lineas.append("! NAT/PAT Overload pendiente de interfaz outside real")
            lineas.append(
                f"! ip nat inside source list {nat_acl_number} interface {wan_interface} overload"
            )
            lineas.append("")

    if office["features"].get("ospf"):
        lineas.append("! OSPF preparado")
        lineas.append(f"router ospf {ospf_process_id}")
        lineas.append(" router-id 1.1.1.1")

        if transit_link:
            lineas.append(
                f" network {transit_link['network']} {transit_link['wildcard']} area {ospf_area}"
            )
        else:
            lineas.append(f"! network <RED_TRANSITO_LAN> <WILDCARD> area {ospf_area}")

        if edge_connection:
            edge_network = edge_connection["network"].split("/")[0]
            lineas.append(f" network {edge_network} 0.0.0.255 area {ospf_area}")

        lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_edge_routers_desde_config(config, output_base_dir):
    gateway_policy = config["global"].get("gateway_policy", "last_usable")

    output_dir = Path(output_base_dir) / "configs" / "routers"
    output_dir.mkdir(parents=True, exist_ok=True)

    archivos_generados = []
    routers_generados = set()

    for office in config["offices"]:
        router_name = office["edge_router"]

        if router_name in routers_generados:
            continue

        vlsm_plan = calcular_vlsm_oficina(office, gateway_policy)

        config_text = generar_config_edge_router(
            router_name=router_name,
            office=office,
            vlsm_plan=vlsm_plan,
            config=config,
        )

        ruta = output_dir / f"{router_name}.txt"
        ruta.write_text(config_text, encoding="utf-8")

        archivos_generados.append(ruta)
        routers_generados.add(router_name)

    return archivos_generados