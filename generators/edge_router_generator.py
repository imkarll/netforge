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


def generar_acl_nat(vlsm_plan):
    lineas = []

    lineas.append("! ACL para NAT/PAT de redes internas")

    for item in vlsm_plan:
        lineas.append(
            f"access-list 1 permit {item['network']} {item['wildcard']}"
        )

    lineas.append("")
    return lineas


def generar_config_edge_router(router_name, office, vlsm_plan, config):
    lineas = []

    management_config = config.get("management", {})
    edge_connection = buscar_conexion_edge_para_router(config, router_name)

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {router_name}")
    lineas.append("")

    if management_config.get("ssh", {}).get("enabled"):
        lineas.extend(generar_bloque_ssh())

    if edge_connection:
        lineas.append("! Interfaz hacia Internet / ISP")
        lineas.append("interface g0/0")
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
        lineas.append("! interface g0/0")
        lineas.append("!  description ENLACE-HACIA-ISP")
        lineas.append("!  ip address <IP_PUBLICA> <MASCARA>")
        lineas.append("!  ip nat outside")
        lineas.append("!  no shutdown")
        lineas.append("!")
        lineas.append("! Ruta por defecto pendiente")
        lineas.append("! ip route 0.0.0.0 0.0.0.0 <NEXT_HOP_ISP>")
        lineas.append("")

    lineas.append("! Enlace interno hacia LAN pendiente de definir")
    lineas.append("! interface g0/1")
    lineas.append("!  description ENLACE-HACIA-LAN")
    lineas.append("!  ip address <IP_TRANSITO_ROUTER> <MASCARA>")
    lineas.append("!  ip nat inside")
    lineas.append("!  no shutdown")
    lineas.append("")

    lineas.append("! Rutas hacia VLANs de la oficina")
    lineas.append("! Ajusta el next-hop cuando definas el enlace interno hacia LAN")
    for item in vlsm_plan:
        lineas.append(f"! ip route {item['network']} {item['mask']} <NEXT_HOP_LAN>")
    lineas.append("")

    if office["features"].get("nat"):
        lineas.extend(generar_acl_nat(vlsm_plan))

        if edge_connection:
            lineas.append("! NAT/PAT Overload")
            lineas.append("ip nat inside source list 1 interface g0/0 overload")
            lineas.append("")
        else:
            lineas.append("! NAT/PAT Overload pendiente de interfaz outside real")
            lineas.append("! ip nat inside source list 1 interface g0/0 overload")
            lineas.append("")

    if office["features"].get("ospf"):
        lineas.append("! OSPF preparado")
        lineas.append("router ospf 1")
        lineas.append(" router-id 1.1.1.1")

        if edge_connection:
            lineas.append(" network 0.0.0.0 255.255.255.255 area 0")
        else:
            lineas.append("! network <RED_TRANSITO_LAN> <WILDCARD> area 0")

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