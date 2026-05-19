from pathlib import Path

from vlsm_calculator import calcular_vlsm


def crear_enlaces_internet(routers, topology):
    enlaces = []

    if topology == "line":
        for indice in range(len(routers) - 1):
            enlaces.append(
                {
                    "nombre": f"Enlace {routers[indice]}-{routers[indice + 1]}",
                    "origen": routers[indice],
                    "destino": routers[indice + 1],
                    "hosts": 2,
                }
            )

    elif topology == "ring":
        for indice in range(len(routers)):
            enlaces.append(
                {
                    "nombre": f"Enlace {routers[indice]}-{routers[(indice + 1) % len(routers)]}",
                    "origen": routers[indice],
                    "destino": routers[(indice + 1) % len(routers)],
                    "hosts": 2,
                }
            )

    else:
        raise ValueError("La topología custom todavía no está implementada.")

    return enlaces


def asignar_ips_a_enlaces(base_network, enlaces):
    necesidades = [
        {
            "nombre": enlace["nombre"],
            "hosts": enlace["hosts"],
        }
        for enlace in enlaces
    ]

    subredes = calcular_vlsm(base_network, necesidades)

    enlaces_con_ips = []

    for enlace, subred in zip(enlaces, subredes):
        enlaces_con_ips.append(
            {
                **enlace,
                "network": subred["red"],
                "prefix": subred["prefijo"],
                "mask": subred["mascara"],
                "wildcard": subred["wildcard"],
                "ip_origen": subred["primer_host"],
                "ip_destino": subred["ultimo_host"],
            }
        )

    return enlaces_con_ips


def obtener_enlaces_router(router, enlaces):
    return [
        enlace
        for enlace in enlaces
        if enlace["origen"] == router or enlace["destino"] == router
    ]


def obtener_edge_connections_router(router, config):
    internet = config.get("internet", {})

    return [
        conexion
        for conexion in internet.get("edge_connections", [])
        if conexion["internet_router"] == router
    ]


def generar_router_id(router_name):
    numero = ""

    for caracter in router_name:
        if caracter.isdigit():
            numero += caracter

    if not numero:
        numero = "99"

    return f"{numero}.{numero}.{numero}.{numero}"


def generar_config_router_internet(router, enlaces, edge_connections, routing_protocol):
    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {router}")
    lineas.append("")

    enlaces_router = obtener_enlaces_router(router, enlaces)

    for indice, enlace in enumerate(enlaces_router):
        interfaz = f"s0/0/{indice}"

        if enlace["origen"] == router:
            ip = enlace["ip_origen"]
            vecino = enlace["destino"]
            es_origen = True
        else:
            ip = enlace["ip_destino"]
            vecino = enlace["origen"]
            es_origen = False

        lineas.append(f"interface {interfaz}")
        lineas.append(f" description ENLACE-HACIA-{vecino}")
        lineas.append(f" ip address {ip} {enlace['mask']}")

        if es_origen:
            lineas.append(" clock rate 64000")

        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

    for indice, conexion in enumerate(edge_connections):
        interfaz = f"g0/{indice}"

        lineas.append(f"interface {interfaz}")
        lineas.append(f" description ENLACE-HACIA-{conexion['enterprise_router']}")
        lineas.append(f" ip address {conexion['internet_ip']} 255.255.255.0")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

    if routing_protocol == "ospf":
        lineas.append("router ospf 1")
        lineas.append(f" router-id {generar_router_id(router)}")

        for enlace in enlaces_router:
            lineas.append(f" network {enlace['network']} {enlace['wildcard']} area 0")

        for conexion in edge_connections:
            red = conexion["network"].split("/")[0]
            lineas.append(f" network {red} 0.0.0.255 area 0")

        lineas.append("")

    elif routing_protocol == "static":
        lineas.append("! Routing estático pendiente de definir según topología")
        lineas.append("")

    else:
        lineas.append("! Sin routing dinámico configurado")
        lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_resumen_internet(config, enlaces):
    internet = config["internet"]
    lineas = []

    lineas.append("=== NETFORGE: RESUMEN INTERNET / ISP ===")
    lineas.append("")
    lineas.append(f"Routers: {', '.join(internet['routers'])}")
    lineas.append(f"Red base: {internet['base_network']}")
    lineas.append(f"Topología: {internet['topology']}")
    lineas.append(f"Routing: {internet['routing_protocol']}")
    lineas.append("")

    lineas.append("Enlaces internos ISP:")

    for enlace in enlaces:
        lineas.append(f"- {enlace['nombre']}")
        lineas.append(f"  Red: {enlace['network']}/{enlace['prefix']}")
        lineas.append(f"  {enlace['origen']}: {enlace['ip_origen']}")
        lineas.append(f"  {enlace['destino']}: {enlace['ip_destino']}")
        lineas.append("")

    if internet.get("edge_connections"):
        lineas.append("Conexiones hacia empresa:")

        for conexion in internet["edge_connections"]:
            lineas.append(
                f"- {conexion['internet_router']} ↔ {conexion['enterprise_router']} | "
                f"{conexion['network']} | "
                f"ISP: {conexion['internet_ip']} | Empresa: {conexion['enterprise_ip']}"
            )

    lineas.append("")

    return "\n".join(lineas)


def generar_internet_desde_config(config, output_base_dir):
    internet = config.get("internet", {})

    if not internet.get("enabled"):
        return []

    output_dir = Path(output_base_dir) / "configs" / "routers"
    output_dir.mkdir(parents=True, exist_ok=True)

    routers = internet["routers"]
    topology = internet["topology"]
    base_network = internet["base_network"]
    routing_protocol = internet["routing_protocol"]

    enlaces = crear_enlaces_internet(routers, topology)
    enlaces = asignar_ips_a_enlaces(base_network, enlaces)

    archivos_generados = []

    for router in routers:
        edge_connections = obtener_edge_connections_router(router, config)

        config_text = generar_config_router_internet(
            router=router,
            enlaces=enlaces,
            edge_connections=edge_connections,
            routing_protocol=routing_protocol,
        )

        ruta = output_dir / f"{router}.txt"
        ruta.write_text(config_text, encoding="utf-8")
        archivos_generados.append(ruta)

    resumen = generar_resumen_internet(config, enlaces)
    resumen_dir = Path(output_base_dir)
    ruta_resumen = resumen_dir / "03_resumen_internet.txt"
    ruta_resumen.write_text(resumen, encoding="utf-8")
    archivos_generados.append(ruta_resumen)

    return archivos_generados