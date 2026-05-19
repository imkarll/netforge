from pathlib import Path

from project_loader import cargar_project_config, listar_project_configs
from vlsm_from_config import generar_plan_vlsm_desde_config
from generators.l3_switch_generator import generar_l3_switches_desde_config
from generators.access_switch_generator import generar_access_switches_desde_config
from generators.edge_router_generator import generar_edge_routers_desde_config


def elegir_project_config():
    configs = listar_project_configs()

    if not configs:
        raise FileNotFoundError("No se encontraron project_config.json dentro de outputs/")

    print("Configs encontradas:")

    for indice, ruta in enumerate(configs, start=1):
        print(f"{indice}. {ruta}")

    while True:
        respuesta = input("Elige una config para resolver [1]: ").strip()

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


def generar_resumen_general(config):
    lineas = []

    lineas.append("=== NETFORGE: PLAN MAESTRO CONFIGURABLE ===")
    lineas.append("")
    lineas.append(f"Proyecto: {config['project_name']}")
    lineas.append(f"Modo: {config['mode']}")
    lineas.append("")

    lineas.append("## 1. Configuración global")
    lineas.append(f"- Política de gateway: {config['global']['gateway_policy']}")
    lineas.append(f"- DNS: {', '.join(config['global']['dns_servers'])}")
    lineas.append(f"- VLSM: {config['global']['use_vlsm']}")
    lineas.append("")

    internet = config["internet"]

    lineas.append("## 2. Internet / ISP")
    lineas.append(f"- Activado: {internet['enabled']}")

    if internet["enabled"]:
        lineas.append(f"- Routers: {', '.join(internet['routers'])}")
        lineas.append(f"- Red base: {internet['base_network']}")
        lineas.append(f"- Topología: {internet['topology']}")
        lineas.append(f"- Routing: {internet['routing_protocol']}")

        if internet["edge_connections"]:
            lineas.append("- Conexiones edge:")

            for conexion in internet["edge_connections"]:
                lineas.append(
                    f"  - {conexion['internet_router']} ↔ "
                    f"{conexion['enterprise_router']} | "
                    f"{conexion['network']}"
                )

    lineas.append("")

    lineas.append("## 3. Oficinas")

    for office in config["offices"]:
        lineas.append("")
        lineas.append(f"### Oficina: {office['name']}")
        lineas.append(f"- Red base: {office['base_network']}")
        lineas.append(f"- Routing inter-VLAN: {office['inter_vlan_routing']}")
        lineas.append(f"- Router borde: {office['edge_router']}")

        if office.get("distribution_switch"):
            lineas.append(f"- Switch distribución/L3: {office['distribution_switch']}")

        lineas.append(f"- Switches acceso: {', '.join(office['access_switches'])}")
        lineas.append("")
        lineas.append("VLANs:")

        for vlan in office["vlans"]:
            lineas.append(
                f"- VLAN {vlan['id']} {vlan['name']} | "
                f"Hosts: {vlan['hosts']} | Tipo: {vlan['type']}"
            )

        lineas.append("")
        lineas.append("Features:")

        for feature, enabled in office["features"].items():
            lineas.append(f"- {feature}: {enabled}")

        lineas.append("")
        lineas.append("Switching:")
        lineas.append(f"- VLAN nativa: {office['switching']['native_vlan']}")
        lineas.append(
            "- VLANs permitidas: "
            + ", ".join(str(vlan) for vlan in office["switching"]["allowed_vlans"])
        )
        lineas.append(f"- EtherChannels: {len(office['switching']['etherchannels'])}")
        lineas.append(f"- STP personalizado: {office['switching']['stp']['enabled']}")

        lineas.append("")
        lineas.append("Seguridad:")
        port_security = office["security"]["port_security"]
        lineas.append(f"- Port Security: {port_security['enabled']}")

        if port_security["enabled"]:
            lineas.append(f"  - Máximo MAC: {port_security['max_mac']}")
            lineas.append(f"  - Violación: {port_security['violation']}")
            lineas.append(f"  - Sticky: {port_security['sticky']}")

    lineas.append("")

    vpn = config["vpn"]

    lineas.append("## 4. VPN")
    lineas.append(f"- Activada: {vpn['enabled']}")

    if vpn["enabled"]:
        lineas.append(f"- Tipo: {vpn['type']}")
        lineas.append(f"- Red base: {vpn['base_network']}")
        lineas.append(f"- Túneles definidos: {len(vpn['tunnels'])}")

    lineas.append("")

    management = config["management"]

    lineas.append("## 5. Gestión")
    lineas.append(f"- SSH: {management['ssh']['enabled']}")

    if management["ssh"]["enabled"]:
        lineas.append(f"  - Dominio: {management['ssh']['domain']}")
        lineas.append(f"  - Usuario: {management['ssh']['user']}")
        lineas.append(f"  - RSA modulus: {management['ssh']['rsa_modulus']}")

    lineas.append(f"- Syslog: {management['syslog']['enabled']}")
    lineas.append(f"- TFTP backup: {management['tftp_backup']['enabled']}")
    lineas.append(f"- NTP: {management['ntp']['enabled']}")
    lineas.append("")

    services = config["services"]

    lineas.append("## 6. Servicios")
    lineas.append(f"- Servidores definidos: {len(services['servers'])}")

    for server in services["servers"]:
        lineas.append(
            f"  - {server['name']} | Tipo: {server['type']} | "
            f"VLAN: {server['vlan']} | IP: {server['ip']} | "
            f"Servicios: {', '.join(server['services'])}"
        )

    lineas.append("")

    lineas.append("## 7. Orden recomendado de implementación")
    lineas.append("1. Validar requisitos del proyecto")
    lineas.append("2. Calcular direccionamiento VLSM")
    lineas.append("3. Crear topología física/lógica en Packet Tracer")
    lineas.append("4. Configurar VLANs y switching base")
    lineas.append("5. Configurar routing inter-VLAN")
    lineas.append("6. Configurar routing hacia routers de borde")
    lineas.append("7. Configurar NAT/PAT si aplica")
    lineas.append("8. Configurar routing dinámico si aplica")
    lineas.append("9. Configurar seguridad: SSH, Port Security, ACLs")
    lineas.append("10. Configurar servicios: DHCP, Syslog, TFTP, NTP")
    lineas.append("11. Configurar VPN si aplica")
    lineas.append("12. Ejecutar checklist de pruebas")
    lineas.append("")

    return "\n".join(lineas)


def guardar_plan_maestro(config, contenido):
    project_slug = config["project_name"].lower().replace(" ", "_")
    project_dir = Path("outputs") / project_slug
    project_dir.mkdir(parents=True, exist_ok=True)

    ruta = project_dir / "01_plan_maestro.txt"
    ruta.write_text(contenido, encoding="utf-8")

    print(f"Plan maestro generado en: {ruta}")


def resolver_proyecto(ruta_config):
    config = cargar_project_config(ruta_config)

    print("\nGenerando plan VLSM...")
    generar_plan_vlsm_desde_config(ruta_config)

    print("Generando plan maestro...")
    contenido = generar_resumen_general(config)
    guardar_plan_maestro(config, contenido)

    project_slug = config["project_name"].lower().replace(" ", "_")
    project_dir = Path("outputs") / project_slug

    print("Generando configs de switches L3...")
    archivos_l3 = generar_l3_switches_desde_config(config, project_dir)

    for archivo in archivos_l3:
        print(f"Config generada: {archivo}")

    print("Generando configs de switches de acceso...")
    archivos_access = generar_access_switches_desde_config(config, project_dir)

    for archivo in archivos_access:
        print(f"Config generada: {archivo}")

    print("Generando configs de routers de borde...")
    archivos_edge = generar_edge_routers_desde_config(config, project_dir)

    for archivo in archivos_edge:
        print(f"Config generada: {archivo}")

    print("\nProyecto resuelto correctamente.")

def main():
    ruta_config = elegir_project_config()
    resolver_proyecto(ruta_config)


if __name__ == "__main__":
    main()