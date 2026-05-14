import ipaddress
from pathlib import Path

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def hosts_necesarios_a_prefijo(hosts_necesarios):
    """
    Calcula el prefijo CIDR mínimo para una cantidad de hosts.
    Ejemplo:
    80 hosts -> /25 porque /26 solo da 62 hosts útiles.
    """
    bits_host = 0

    while (2 ** bits_host) - 2 < hosts_necesarios:
        bits_host += 1

    return 32 - bits_host


def calcular_vlsm(red_base, necesidades):
    """
    red_base: string tipo "192.168.1.0/24"
    necesidades: lista de diccionarios:
        [
            {"nombre": "VLAN 20 Usuarios", "hosts": 80},
            {"nombre": "VLAN 10 CPD", "hosts": 20},
        ]
    """

    red_principal = ipaddress.ip_network(red_base, strict=False)

    # Ordenar de mayor a menor necesidad
    necesidades_ordenadas = sorted(
        necesidades,
        key=lambda item: item["hosts"],
        reverse=True,
    )

    subredes_generadas = []
    siguiente_ip = int(red_principal.network_address)

    for necesidad in necesidades_ordenadas:
        nombre = necesidad["nombre"]
        hosts = necesidad["hosts"]

        prefijo = hosts_necesarios_a_prefijo(hosts)

        # Alinear la IP inicial al tamaño correcto de bloque
        tamano_bloque = 2 ** (32 - prefijo)

        if siguiente_ip % tamano_bloque != 0:
            siguiente_ip = ((siguiente_ip // tamano_bloque) + 1) * tamano_bloque

        subred = ipaddress.ip_network((siguiente_ip, prefijo), strict=False)

        if not subred.subnet_of(red_principal):
            raise ValueError(f"No hay espacio suficiente para {nombre} con {hosts} hosts")

        hosts_utiles = subred.num_addresses - 2

        subredes_generadas.append(
            {
                "nombre": nombre,
                "hosts_requeridos": hosts,
                "red": str(subred.network_address),
                "prefijo": subred.prefixlen,
                "mascara": str(subred.netmask),
                "wildcard": str(subred.hostmask),
                "primer_host": str(list(subred.hosts())[0]),
                "ultimo_host": str(list(subred.hosts())[-1]),
                "broadcast": str(subred.broadcast_address),
                "gateway_recomendado": str(list(subred.hosts())[-1]),
                "hosts_utiles": hosts_utiles,
            }
        )

        siguiente_ip = int(subred.broadcast_address) + 1

    return subredes_generadas


def generar_texto_resultado(titulo, subredes):
    lineas = []

    lineas.append(f"\n=== {titulo} ===\n")

    for subred in subredes:
        lineas.append(f"{subred['nombre']}")
        lineas.append(f"  Red: {subred['red']}/{subred['prefijo']}")
        lineas.append(f"  Máscara: {subred['mascara']}")
        lineas.append(f"  Wildcard: {subred['wildcard']}")
        lineas.append(f"  Hosts requeridos: {subred['hosts_requeridos']}")
        lineas.append(f"  Hosts útiles: {subred['hosts_utiles']}")
        lineas.append(f"  Primer host: {subred['primer_host']}")
        lineas.append(f"  Último host: {subred['ultimo_host']}")
        lineas.append(f"  Gateway recomendado: {subred['gateway_recomendado']}")
        lineas.append(f"  Broadcast: {subred['broadcast']}")
        lineas.append("")

    return "\n".join(lineas)


def imprimir_resultado(titulo, subredes):
    print(generar_texto_resultado(titulo, subredes))

