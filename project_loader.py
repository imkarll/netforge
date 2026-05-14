import json
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("outputs")


def cargar_project_config(ruta_config):
    ruta = Path(ruta_config)

    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo de configuración: {ruta}")

    if not ruta.is_file():
        raise ValueError(f"La ruta no apunta a un archivo válido: {ruta}")

    with ruta.open("r", encoding="utf-8") as archivo:
        config = json.load(archivo)

    validar_project_config(config)

    return config


def validar_project_config(config):
    campos_obligatorios = [
        "project_name",
        "mode",
        "global",
        "internet",
        "offices",
        "vpn",
        "management",
        "services",
    ]

    for campo in campos_obligatorios:
        if campo not in config:
            raise ValueError(f"Falta el campo obligatorio: {campo}")

    if not isinstance(config["offices"], list):
        raise ValueError("El campo 'offices' debe ser una lista.")

    if len(config["offices"]) == 0:
        raise ValueError("El proyecto debe tener al menos una oficina.")

    for office in config["offices"]:
        validar_oficina(office)


def validar_oficina(office):
    campos_obligatorios = [
        "name",
        "base_network",
        "inter_vlan_routing",
        "edge_router",
        "access_switches",
        "vlans",
        "features",
        "switching",
        "security",
    ]

    for campo in campos_obligatorios:
        if campo not in office:
            raise ValueError(f"En oficina falta el campo obligatorio: {campo}")

    if not isinstance(office["vlans"], list):
        raise ValueError(f"Las VLANs de la oficina {office['name']} deben ser una lista.")

    if len(office["vlans"]) == 0:
        raise ValueError(f"La oficina {office['name']} debe tener al menos una VLAN.")

    vlan_ids = []

    for vlan in office["vlans"]:
        validar_vlan(vlan)
        vlan_ids.append(vlan["id"])

    if len(vlan_ids) != len(set(vlan_ids)):
        raise ValueError(f"La oficina {office['name']} tiene VLAN IDs duplicados.")


def validar_vlan(vlan):
    campos_obligatorios = [
        "id",
        "name",
        "hosts",
        "type",
    ]

    for campo in campos_obligatorios:
        if campo not in vlan:
            raise ValueError(f"En VLAN falta el campo obligatorio: {campo}")

    if not isinstance(vlan["id"], int):
        raise ValueError(f"El ID de VLAN debe ser número entero: {vlan}")

    if vlan["id"] < 1 or vlan["id"] > 4094:
        raise ValueError(f"ID de VLAN fuera de rango: {vlan['id']}")

    if not isinstance(vlan["hosts"], int):
        raise ValueError(f"Los hosts de VLAN deben ser número entero: {vlan}")

    if vlan["hosts"] < 1:
        raise ValueError(f"Los hosts de VLAN deben ser mayor que 0: {vlan}")


def obtener_ruta_config_por_nombre(nombre_proyecto):
    project_slug = nombre_proyecto.lower().replace(" ", "_")
    return DEFAULT_OUTPUT_DIR / project_slug / "project_config.json"


def listar_project_configs():
    configs = []

    if not DEFAULT_OUTPUT_DIR.exists():
        return configs

    for ruta in DEFAULT_OUTPUT_DIR.glob("*/project_config.json"):
        configs.append(ruta)

    return configs


def mostrar_resumen_config(config):
    print("=== NETFORGE: PROJECT CONFIG LOADED ===")
    print("")
    print(f"Proyecto: {config['project_name']}")
    print(f"Modo: {config['mode']}")
    print(f"Oficinas: {len(config['offices'])}")
    print("")

    internet = config["internet"]

    print("Internet/ISP:")
    print(f"- Activado: {internet['enabled']}")

    if internet["enabled"]:
        print(f"- Routers: {', '.join(internet['routers'])}")
        print(f"- Red base: {internet['base_network']}")
        print(f"- Topología: {internet['topology']}")
        print(f"- Routing: {internet['routing_protocol']}")

    print("")

    print("Oficinas:")

    for office in config["offices"]:
        print(f"- {office['name']}")
        print(f"  Red base: {office['base_network']}")
        print(f"  Routing inter-VLAN: {office['inter_vlan_routing']}")
        print(f"  Router borde: {office['edge_router']}")
        print(f"  Switches acceso: {', '.join(office['access_switches'])}")
        print(f"  VLANs: {len(office['vlans'])}")

        for vlan in office["vlans"]:
            print(
                f"    VLAN {vlan['id']} | {vlan['name']} | "
                f"Hosts: {vlan['hosts']} | Tipo: {vlan['type']}"
            )

        print("")

    vpn = config["vpn"]
    print("VPN:")
    print(f"- Activada: {vpn['enabled']}")

    if vpn["enabled"]:
        print(f"- Tipo: {vpn['type']}")
        print(f"- Red base: {vpn['base_network']}")

    print("")


def main():
    configs = listar_project_configs()

    if not configs:
        print("No se encontraron project_config.json dentro de outputs/")
        return

    print("Configs encontradas:")

    for indice, ruta in enumerate(configs, start=1):
        print(f"{indice}. {ruta}")

    while True:
        respuesta = input("Elige una config para cargar [1]: ").strip()

        if not respuesta:
            indice = 1
        else:
            try:
                indice = int(respuesta)
            except ValueError:
                print("Introduce un número válido.")
                continue

        if 1 <= indice <= len(configs):
            ruta_config = configs[indice - 1]
            break

        print("Opción no válida.")

    config = cargar_project_config(ruta_config)
    mostrar_resumen_config(config)


if __name__ == "__main__":
    main()