from pathlib import Path


OUTPUT_DIR = Path("outputs/edge_routers")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ROUTERS_BORDE = {
    "R1": {
        "descripcion": "Router borde oficina central",
        "interfaz_internet": "g0/0",
        "ip_internet": "80.0.0.1",
        "mascara_internet": "255.255.255.0",
        "gateway_internet": "80.0.0.2",
        "vecino_internet": "I1",
        "inside_description": "HACIA-LAN-CENTRAL",
        "red_lan": "192.168.1.0",
        "wildcard_lan": "0.0.0.255",
    },
    "R2": {
        "descripcion": "Router borde oficina remota",
        "interfaz_internet": "g0/0",
        "ip_internet": "90.0.0.2",
        "mascara_internet": "255.255.255.0",
        "gateway_internet": "90.0.0.1",
        "vecino_internet": "I4",
        "inside_description": "HACIA-LAN-REMOTA",
        "red_lan": "172.20.0.0",
        "wildcard_lan": "0.0.0.255",
    },
}

def generar_config_router_borde(nombre_router, datos):
    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {nombre_router}")
    lineas.append("")

    lineas.append("! Enlace hacia Internet / ISP")
    lineas.append(f"interface {datos['interfaz_internet']}")
    lineas.append(f" description ENLACE-HACIA-{datos['vecino_internet']}")
    lineas.append(f" ip address {datos['ip_internet']} {datos['mascara_internet']}")
    lineas.append(" ip nat outside")
    lineas.append(" no shutdown")
    lineas.append("exit")
    lineas.append("")

    lineas.append("! Ruta por defecto hacia Internet")
    lineas.append(f"ip route 0.0.0.0 0.0.0.0 {datos['gateway_internet']}")
    lineas.append("")

    lineas.append("! NAT/PAT Overload")
    lineas.append(f"access-list 1 permit {datos['red_lan']} {datos['wildcard_lan']}")
    lineas.append(f"ip nat inside source list 1 interface {datos['interfaz_internet']} overload")
    lineas.append("")

    lineas.append("! Interfaz interna pendiente de definir")
    lineas.append("! Se configurará al integrar la oficina correspondiente")
    lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_resumen():
    lineas = []

    lineas.append("=== NETFORGE: RESUMEN ROUTERS DE BORDE ===")
    lineas.append("")

    for router, datos in ROUTERS_BORDE.items():
        lineas.append(router)
        lineas.append(f"  Descripción: {datos['descripcion']}")
        lineas.append(f"  Interfaz Internet: {datos['interfaz_internet']}")
        lineas.append(f"  IP Internet: {datos['ip_internet']} {datos['mascara_internet']}")
        lineas.append(f"  Vecino Internet: {datos['vecino_internet']}")
        lineas.append(f"  Ruta por defecto hacia: {datos['gateway_internet']}")
        lineas.append(f"  Red LAN para NAT: {datos['red_lan']} {datos['wildcard_lan']}")
        lineas.append("")

    return "\n".join(lineas)


def generar_configs_routers_borde():
    for router, datos in ROUTERS_BORDE.items():
        config = generar_config_router_borde(router, datos)

        ruta = OUTPUT_DIR / f"{router}.txt"
        ruta.write_text(config, encoding="utf-8")

        print(f"Config generada: {ruta}")

    resumen = generar_resumen()
    ruta_resumen = OUTPUT_DIR / "RESUMEN_EDGE_ROUTERS.txt"
    ruta_resumen.write_text(resumen, encoding="utf-8")

    print(f"Resumen generado: {ruta_resumen}")


def main():
    generar_configs_routers_borde()
    print("\nGeneración de routers de borde completada.")


if __name__ == "__main__":
    main()