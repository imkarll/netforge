from pathlib import Path

from project_loader import cargar_project_config, listar_project_configs
from vlsm_calculator import calcular_vlsm


def elegir_project_config():
    configs = listar_project_configs()

    if not configs:
        raise FileNotFoundError("No se encontraron project_config.json dentro de outputs/")

    print("Configs encontradas:")

    for indice, ruta in enumerate(configs, start=1):
        print(f"{indice}. {ruta}")

    while True:
        respuesta = input("Elige una config para calcular VLSM [1]: ").strip()

        if not respuesta:
            indice = 1
        else:
            try:
                indice = int(respuesta)
            except ValueError:
                print("Introduce un número válido.")
                continue

        if 1 <= indice <= len(configs):
            return configs[indice - 1]

        print("Opción no válida.")


def obtener_gateway(subred, gateway_policy):
    if gateway_policy == "first_usable":
        return subred["primer_host"]

    if gateway_policy == "last_usable":
        return subred["ultimo_host"]

    # De momento manual no está implementado en el wizard.
    # Usamos last_usable como fallback seguro.
    return subred["ultimo_host"]


def construir_necesidades_desde_vlans(vlans):
    necesidades = []

    for vlan in vlans:
        necesidades.append(
            {
                "nombre": f"VLAN {vlan['id']} {vlan['name']}",
                "hosts": vlan["hosts"],
                "vlan_id": vlan["id"],
                "vlan_name": vlan["name"],
                "vlan_type": vlan["type"],
            }
        )

    return necesidades


def calcular_vlsm_oficina(office, gateway_policy):
    necesidades = construir_necesidades_desde_vlans(office["vlans"])
    subredes = calcular_vlsm(office["base_network"], necesidades)

    resultado = []

    for vlan, subred in zip(office["vlans"], subredes):
        gateway = obtener_gateway(subred, gateway_policy)

        resultado.append(
            {
                "office": office["name"],
                "vlan_id": vlan["id"],
                "vlan_name": vlan["name"],
                "vlan_type": vlan["type"],
                "hosts_required": vlan["hosts"],
                "network": subred["red"],
                "prefix": subred["prefijo"],
                "mask": subred["mascara"],
                "wildcard": subred["wildcard"],
                "usable_hosts": subred["hosts_utiles"],
                "first_host": subred["primer_host"],
                "last_host": subred["ultimo_host"],
                "gateway": gateway,
                "broadcast": subred["broadcast"],
            }
        )

    return resultado


def generar_texto_plan_vlsm(config, planes_por_oficina):
    lineas = []

    lineas.append("=== NETFORGE: PLAN VLSM DESDE PROJECT CONFIG ===")
    lineas.append("")
    lineas.append(f"Proyecto: {config['project_name']}")
    lineas.append(f"Modo: {config['mode']}")
    lineas.append(f"Politica de gateway: {config['global']['gateway_policy']}")
    lineas.append("")

    for office_name, plan in planes_por_oficina.items():
        lineas.append(f"=== OFICINA: {office_name.upper()} ===")
        lineas.append("")

        for item in plan:
            lineas.append(f"VLAN {item['vlan_id']} {item['vlan_name']}")
            lineas.append(f"  Tipo: {item['vlan_type']}")
            lineas.append(f"  Red: {item['network']}/{item['prefix']}")
            lineas.append(f"  Mascara: {item['mask']}")
            lineas.append(f"  Wildcard: {item['wildcard']}")
            lineas.append(f"  Hosts requeridos: {item['hosts_required']}")
            lineas.append(f"  Hosts utiles: {item['usable_hosts']}")
            lineas.append(f"  Primer host: {item['first_host']}")
            lineas.append(f"  Ultimo host: {item['last_host']}")
            lineas.append(f"  Gateway: {item['gateway']}")
            lineas.append(f"  Broadcast: {item['broadcast']}")
            lineas.append("")

    return "\n".join(lineas)


def generar_plan_vlsm_desde_config(ruta_config):
    config = cargar_project_config(ruta_config)

    gateway_policy = config["global"].get("gateway_policy", "last_usable")

    planes_por_oficina = {}

    for office in config["offices"]:
        planes_por_oficina[office["name"]] = calcular_vlsm_oficina(
            office,
            gateway_policy,
        )

    contenido = generar_texto_plan_vlsm(config, planes_por_oficina)

    project_dir = Path(ruta_config).parent
    ruta_salida = project_dir / "02_plan_vlsm.txt"
    ruta_salida.write_text(contenido, encoding="utf-8")

    print(f"Plan VLSM generado en: {ruta_salida}")

    return planes_por_oficina


def main():
    ruta_config = elegir_project_config()
    generar_plan_vlsm_desde_config(ruta_config)


if __name__ == "__main__":
    main()