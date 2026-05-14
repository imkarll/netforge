from pathlib import Path

from vlsm_calculator import calcular_vlsm


OUTPUT_DIR = Path("outputs/internet_ospf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ROUTERS_INTERNET = ["I1", "I2", "I3", "I4", "I5", "I6"]


def crear_enlaces_anillo(routers):
    enlaces = []

    for indice in range(len(routers)):
        origen = routers[indice]
        destino = routers[(indice + 1) % len(routers)]

        enlaces.append(
            {
                "nombre": f"Enlace {origen}-{destino}",
                "origen": origen,
                "destino": destino,
                "hosts": 2,
            }
        )

    return enlaces


def asignar_ips_a_enlaces(red_base, enlaces):
    necesidades = [
        {
            "nombre": enlace["nombre"],
            "hosts": enlace["hosts"],
        }
        for enlace in enlaces
    ]

    subredes = calcular_vlsm(red_base, necesidades)

    enlaces_con_ips = []

    for enlace, subred in zip(enlaces, subredes):
        enlaces_con_ips.append(
            {
                **enlace,
                "red": subred["red"],
                "prefijo": subred["prefijo"],
                "mascara": subred["mascara"],
                "wildcard": subred["wildcard"],
                "ip_origen": subred["primer_host"],
                "ip_destino": subred["ultimo_host"],
            }
        )

    return enlaces_con_ips


def obtener_enlaces_por_router(router, enlaces):
    resultado = []

    for enlace in enlaces:
        if enlace["origen"] == router or enlace["destino"] == router:
            resultado.append(enlace)

    return resultado


def generar_config_router(router, enlaces):
    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {router}")
    lineas.append("")

    enlaces_router = obtener_enlaces_por_router(router, enlaces)

    for indice, enlace in enumerate(enlaces_router):
        interfaz = f"s0/0/{indice}"

        if enlace["origen"] == router:
            ip = enlace["ip_origen"]
            vecino = enlace["destino"]
        else:
            ip = enlace["ip_destino"]
            vecino = enlace["origen"]

        lineas.append(f"interface {interfaz}")
        lineas.append(f" description ENLACE-HACIA-{vecino}")
        lineas.append(f" ip address {ip} {enlace['mascara']}")

        if enlace["origen"] == router:
            lineas.append(" clock rate 64000")

        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

    lineas.append("router ospf 1")
    lineas.append(f" router-id {router.replace('I', '')}.{router.replace('I', '')}.{router.replace('I', '')}.{router.replace('I', '')}")

    for enlace in enlaces_router:
        lineas.append(f" network {enlace['red']} {enlace['wildcard']} area 0")

    lineas.append("")
    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_configs_internet(red_base="70.0.0.0/24", routers=None):
    if routers is None:
        routers = ROUTERS_INTERNET

    enlaces = crear_enlaces_anillo(routers)
    enlaces = asignar_ips_a_enlaces(red_base, enlaces)

    for router in routers:
        config = generar_config_router(router, enlaces)

        ruta = OUTPUT_DIR / f"{router}.txt"
        ruta.write_text(config, encoding="utf-8")

        print(f"Config generada: {ruta}")

    return enlaces


def generar_resumen_enlaces(enlaces):
    lineas = []

    lineas.append("=== NETFORGE: RESUMEN INTERNET OSPF ===")
    lineas.append("")

    for enlace in enlaces:
        lineas.append(f"{enlace['nombre']}")
        lineas.append(f"  Red: {enlace['red']}/{enlace['prefijo']}")
        lineas.append(f"  {enlace['origen']}: {enlace['ip_origen']}")
        lineas.append(f"  {enlace['destino']}: {enlace['ip_destino']}")
        lineas.append(f"  Mascara: {enlace['mascara']}")
        lineas.append("")

    contenido = "\n".join(lineas)

    ruta = OUTPUT_DIR / "RESUMEN_INTERNET.txt"
    ruta.write_text(contenido, encoding="utf-8")

    print(f"Resumen generado: {ruta}")


def main():
    enlaces = generar_configs_internet()
    generar_resumen_enlaces(enlaces)

    print("\nGeneración Internet OSPF completada.")


if __name__ == "__main__":
    main()