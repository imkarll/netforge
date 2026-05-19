import json
from pathlib import Path


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def preguntar_texto(mensaje, valor_default=None):
    if valor_default is not None:
        respuesta = input(f"{mensaje} [{valor_default}]: ").strip()
        return respuesta if respuesta else valor_default

    return input(f"{mensaje}: ").strip()


def preguntar_entero(mensaje, valor_default=None):
    while True:
        if valor_default is not None:
            respuesta = input(f"{mensaje} [{valor_default}]: ").strip()
            if not respuesta:
                return valor_default
        else:
            respuesta = input(f"{mensaje}: ").strip()

        try:
            return int(respuesta)
        except ValueError:
            print("Introduce un número válido.")


def preguntar_si_no(mensaje, valor_default="n"):
    while True:
        respuesta = input(f"{mensaje} (s/n) [{valor_default}]: ").strip().lower()

        if not respuesta:
            respuesta = valor_default

        if respuesta in ["s", "si", "sí", "y", "yes"]:
            return True

        if respuesta in ["n", "no"]:
            return False

        print("Responde con s/n.")


def preguntar_opcion(mensaje, opciones, valor_default=1):
    print(f"\n{mensaje}")

    for indice, opcion in enumerate(opciones, start=1):
        print(f"{indice}. {opcion}")

    while True:
        respuesta = input(f"Elige una opción [{valor_default}]: ").strip()

        if not respuesta:
            return opciones[valor_default - 1]

        try:
            indice = int(respuesta)

            if 1 <= indice <= len(opciones):
                return opciones[indice - 1]

        except ValueError:
            pass

        print("Opción no válida.")


def crear_global_config():
    gateway_policy = preguntar_opcion(
        "Política de gateway para subredes",
        ["first_usable", "last_usable", "manual"],
        2,
    )

    dns = preguntar_texto("DNS principal", "8.8.8.8")

    return {
        "gateway_policy": gateway_policy,
        "dns_servers": [dns],
        "use_vlsm": True,
        "default_subnet_for_p2p": 30,
    }


def crear_internet_config():
    enabled = preguntar_si_no("¿Deseas simular Internet/ISP?", "s")

    if not enabled:
        return {
            "enabled": False,
            "routers": [],
            "base_network": None,
            "topology": None,
            "routing_protocol": None,
            "edge_connections": [],
        }

    cantidad_routers = preguntar_entero("Cantidad de routers de Internet", 3)
    prefijo = preguntar_texto("Prefijo de routers de Internet", "I")

    routers = [f"{prefijo}{numero}" for numero in range(1, cantidad_routers + 1)]

    base_network = preguntar_texto("Red base de Internet", "70.0.0.0/24")

    topology = preguntar_opcion(
        "Topología de Internet",
        ["ring", "line", "custom"],
        1,
    )

    routing_protocol = preguntar_opcion(
        "Protocolo de routing en Internet",
        ["ospf", "static", "none"],
        1,
    )

    edge_connections = []

    if preguntar_si_no("¿Deseas definir conexiones entre Internet y routers de empresa?", "s"):
        cantidad = preguntar_entero("Cantidad de conexiones edge", 1)

        for numero in range(1, cantidad + 1):
            print(f"\nConexión edge {numero}")

            edge_connections.append(
                {
                    "internet_router": preguntar_texto("Router de Internet", routers[0]),
                    "enterprise_router": preguntar_texto("Router de empresa", f"R{numero}"),
                    "network": preguntar_texto("Red del enlace", f"80.0.{numero - 1}.0/24"),
                    "internet_ip": preguntar_texto("IP del router Internet"),
                    "enterprise_ip": preguntar_texto("IP del router empresa"),
                }
            )

    return {
        "enabled": True,
        "routers": routers,
        "base_network": base_network,
        "topology": topology,
        "routing_protocol": routing_protocol,
        "edge_connections": edge_connections,
    }


def crear_vlan(numero):
    print(f"\nVLAN {numero}")

    vlan_id = preguntar_entero("ID de VLAN")
    nombre = preguntar_texto("Nombre de VLAN").upper()
    hosts = preguntar_entero("Hosts necesarios")

    vlan_type = preguntar_opcion(
        "Tipo de VLAN",
        ["users", "servers", "management", "guest", "voice", "it", "custom"],
        1,
    )

    return {
        "id": vlan_id,
        "name": nombre,
        "hosts": hosts,
        "type": vlan_type,
    }


def crear_features():
    print("\nFeatures de la oficina")

    return {
        "dhcp": preguntar_si_no("¿Usar DHCP?", "n"),
        "nat": preguntar_si_no("¿Usar NAT/PAT?", "s"),
        "ospf": preguntar_si_no("¿Publicar redes con OSPF?", "s"),
        "ssh": preguntar_si_no("¿Habilitar SSH?", "s"),
        "syslog": preguntar_si_no("¿Usar Syslog?", "n"),
        "tftp_backup": preguntar_si_no("¿Usar backup TFTP?", "n"),
        "etherchannel": preguntar_si_no("¿Usar EtherChannel?", "n"),
        "port_security": preguntar_si_no("¿Usar Port Security?", "n"),
        "stp": preguntar_si_no("¿Configurar STP personalizado?", "n"),
    }


def crear_switching_config(access_switches, vlans):
    vlan_ids = [vlan["id"] for vlan in vlans]

    switching = {
        "native_vlan": 1,
        "allowed_vlans": sorted(set(vlan_ids)),
        "etherchannels": [],
        "stp": {
            "enabled": False,
            "roots": [],
        },
    }

    if preguntar_si_no("¿Configurar EtherChannels para esta oficina?", "n"):
        cantidad = preguntar_entero("Cantidad de EtherChannels", len(access_switches))

        for numero in range(1, cantidad + 1):
            print(f"\nEtherChannel {numero}")

            interfaces_from = preguntar_texto(
                "Interfaces origen separadas por coma",
                "fa0/23,fa0/24",
            ).split(",")

            interfaces_to = preguntar_texto(
                "Interfaces destino separadas por coma",
                "fa0/1,fa0/2",
            ).split(",")

            switching["etherchannels"].append(
                {
                    "from": preguntar_texto(
                        "Switch origen",
                        access_switches[0] if access_switches else "SW1",
                    ),
                    "to": preguntar_texto("Switch destino", "SW-DIST"),
                    "interfaces_from": [interface.strip() for interface in interfaces_from],
                    "interfaces_to": [interface.strip() for interface in interfaces_to],
                    "mode": preguntar_opcion(
                        "Modo EtherChannel",
                        ["active", "passive", "desirable", "auto", "on"],
                        1,
                    ),
                    "port_channel": preguntar_entero("Número de Port-channel", numero),
                }
            )

    if preguntar_si_no("¿Configurar STP root por VLAN?", "n"):
        switching["stp"]["enabled"] = True
        cantidad_roots = preguntar_entero("Cantidad de reglas STP root", 1)

        for numero in range(1, cantidad_roots + 1):
            print(f"\nRegla STP root {numero}")

            switching["stp"]["roots"].append(
                {
                    "vlan": preguntar_entero("VLAN"),
                    "root": preguntar_texto("Switch root"),
                }
            )

    return switching


def crear_security_config():
    port_security_enabled = preguntar_si_no("¿Configurar Port Security?", "n")

    return {
        "port_security": {
            "enabled": port_security_enabled,
            "max_mac": preguntar_entero("Máximo de MAC por puerto", 2)
            if port_security_enabled
            else None,
            "violation": preguntar_opcion(
                "Modo de violación",
                ["shutdown", "restrict", "protect"],
                1,
            )
            if port_security_enabled
            else None,
            "sticky": preguntar_si_no("¿Usar MAC sticky?", "s")
            if port_security_enabled
            else False,
        },
        "acls": [],
    }


def crear_oficina(numero):
    print(f"\n=== OFICINA {numero} ===")

    name = preguntar_texto("Nombre de la oficina", f"oficina_{numero}").lower()
    base_network = preguntar_texto("Red base de la oficina", "192.168.1.0/24")

    inter_vlan_routing = preguntar_opcion(
        "Tipo de routing inter-VLAN",
        ["layer3_switch", "router_on_a_stick", "none"],
        1,
    )

    edge_router = preguntar_texto("Router de borde de esta oficina", f"R{numero}")

    distribution_switch = None

    if inter_vlan_routing == "layer3_switch":
        distribution_switch = preguntar_texto("Switch de distribución/capa 3", "SW-DIST")

    cantidad_switches = preguntar_entero("Cantidad de switches de acceso", 1)
    prefijo_switch = preguntar_texto("Prefijo de switches de acceso", "SW")

    access_switches = [
        f"{prefijo_switch}{indice}"
        for indice in range(1, cantidad_switches + 1)
    ]

    cantidad_vlans = preguntar_entero("Cantidad de VLANs de usuario/servicio", 1)

    vlans = []

    for indice in range(1, cantidad_vlans + 1):
        vlans.append(crear_vlan(indice))

    if preguntar_si_no("¿Añadir VLAN de administración?", "s"):
        admin_vlan_id = preguntar_entero("ID VLAN administración", 1)
        admin_hosts = preguntar_entero("Hosts administración", max(2, cantidad_switches + 2))

        vlans.append(
            {
                "id": admin_vlan_id,
                "name": "ADMINISTRACION",
                "hosts": admin_hosts,
                "type": "management",
            }
        )

    features = crear_features()
    switching = crear_switching_config(access_switches, vlans)
    security = crear_security_config()

    return {
        "name": name,
        "base_network": base_network,
        "inter_vlan_routing": inter_vlan_routing,
        "edge_router": edge_router,
        "distribution_switch": distribution_switch,
        "access_switches": access_switches,
        "vlans": vlans,
        "features": features,
        "switching": switching,
        "security": security,
    }


def crear_vpn_config():
    enabled = preguntar_si_no("¿Usar VPN entre sedes?", "n")

    if not enabled:
        return {
            "enabled": False,
            "type": None,
            "base_network": None,
            "tunnels": [],
        }

    vpn_type = preguntar_opcion("Tipo de VPN", ["gre", "ipsec", "none"], 1)
    base_network = preguntar_texto("Red base de túneles VPN", "172.16.0.0/16")

    return {
        "enabled": True,
        "type": vpn_type,
        "base_network": base_network,
        "tunnels": [],
    }


def crear_management_config():
    ssh_enabled = preguntar_si_no("¿Configurar SSH global?", "s")

    ssh = {
        "enabled": ssh_enabled,
    }

    if ssh_enabled:
        ssh.update(
            {
                "domain": preguntar_texto("Dominio SSH", "netforge.local"),
                "user": preguntar_texto("Usuario SSH", "admin"),
                "secret": preguntar_texto("Secret SSH", "Cisco123"),
                "rsa_modulus": preguntar_entero("RSA modulus", 1024),
            }
        )

    syslog_enabled = preguntar_si_no("¿Configurar Syslog global?", "n")
    tftp_enabled = preguntar_si_no("¿Configurar TFTP global?", "n")
    ntp_enabled = preguntar_si_no("¿Configurar NTP?", "n")

    return {
        "ssh": ssh,
        "syslog": {
            "enabled": syslog_enabled,
            "server_ip": preguntar_texto("IP servidor Syslog") if syslog_enabled else None,
            "trap_level": "warnings" if syslog_enabled else None,
        },
        "tftp_backup": {
            "enabled": tftp_enabled,
            "server_ip": preguntar_texto("IP servidor TFTP") if tftp_enabled else None,
        },
        "ntp": {
            "enabled": ntp_enabled,
            "server_ip": preguntar_texto("IP servidor NTP") if ntp_enabled else None,
        },
    }


def crear_services_config():
    servers = []

    if preguntar_si_no("¿Deseas definir servidores?", "n"):
        cantidad = preguntar_entero("Cantidad de servidores", 1)

        for numero in range(1, cantidad + 1):
            print(f"\nServidor {numero}")

            services = preguntar_texto("Servicios separados por coma", "http").split(",")

            servers.append(
                {
                    "name": preguntar_texto("Nombre del servidor", f"SERVER{numero}"),
                    "type": preguntar_opcion("Tipo de servidor", ["web", "syslog", "tftp", "dns", "dhcp", "custom"], 1),
                    "vlan": preguntar_entero("VLAN del servidor"),
                    "ip": preguntar_texto("IP del servidor"),
                    "services": [service.strip() for service in services],
                }
            )

    return {
        "servers": servers,
    }

def crear_topology_config(offices):
    print("\nTopología interna")

    transit_links = []

    if preguntar_si_no("¿Generar enlaces de tránsito entre router borde y switch L3?", "s"):
        for office in offices:
            if office["inter_vlan_routing"] != "layer3_switch":
                continue

            edge_router = office["edge_router"]
            distribution_switch = office.get("distribution_switch") or "SW-DIST"

            print(f"\nEnlace de tránsito para oficina {office['name']}")
            print(f"{edge_router} ↔ {distribution_switch}")

            network = preguntar_texto("Red de tránsito /30", "192.168.255.0/30")
            from_interface = preguntar_texto(f"Interfaz en {edge_router}", "g0/1")
            to_interface = preguntar_texto(f"Interfaz en {distribution_switch}", "g0/1")
            from_ip = preguntar_texto(f"IP en {edge_router}", "192.168.255.1")
            to_ip = preguntar_texto(f"IP en {distribution_switch}", "192.168.255.2")

            transit_links.append(
                {
                    "name": f"{edge_router}-{distribution_switch}",
                    "office": office["name"],
                    "from_device": edge_router,
                    "to_device": distribution_switch,
                    "from_interface": from_interface,
                    "to_interface": to_interface,
                    "network": network,
                    "from_ip": from_ip,
                    "to_ip": to_ip,
                    "mask": "255.255.255.252",
                    "wildcard": "0.0.0.3",
                    "description": f"ENLACE-{edge_router}-{distribution_switch}",
                }
            )

    return {
        "transit_links": transit_links,
        "interface_defaults": {
            "edge_wan_interface": "g0/0",
            "edge_lan_interface": "g0/1",
            "access_trunk_interface": "fa0/24",
        },
        "routing_defaults": {
            "ospf_process_id": 1,
            "ospf_area": 0,
            "router_id_mode": "auto",
        },
        "nat_defaults": {
            "acl_number": 1,
            "type": "pat",
        },
    }

def crear_project_config():
    print("=== NETFORGE PROJECT WIZARD ===")
    print("Creador configurable de proyectos CCNA.\n")

    project_name = preguntar_texto("Nombre del proyecto", "Proyecto_NetForge")

    mode = preguntar_opcion(
        "Modo del proyecto",
        ["basic", "intermediate", "advanced", "final_project"],
        2,
    )

    global_config = crear_global_config()
    internet = crear_internet_config()

    cantidad_oficinas = preguntar_entero("Cantidad de oficinas/sedes", 1)

    offices = []

    for numero in range(1, cantidad_oficinas + 1):
        offices.append(crear_oficina(numero))

    vpn = crear_vpn_config()
    management = crear_management_config()
    services = crear_services_config()
    topology = crear_topology_config(offices)

    return {
        "project_name": project_name,
        "mode": mode,
        "global": global_config,
        "internet": internet,
        "offices": offices,
        "vpn": vpn,
        "management": management,
        "services": services,
        "topology": topology,
    }


def guardar_project_config(project_config):
    project_slug = project_config["project_name"].lower().replace(" ", "_")
    project_dir = OUTPUT_DIR / project_slug
    project_dir.mkdir(parents=True, exist_ok=True)

    ruta = project_dir / "project_config.json"

    contenido = json.dumps(project_config, indent=4, ensure_ascii=False)
    ruta.write_text(contenido, encoding="utf-8")

    print(f"\nConfig del proyecto guardada en: {ruta}")


def main():
    project_config = crear_project_config()
    guardar_project_config(project_config)

    print("\nProject wizard completado.")


if __name__ == "__main__":
    main()