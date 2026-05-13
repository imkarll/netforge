prompt = input("Describe la red: ").lower()

configs = []

configs.append("=== CONFIGURACIÓN GENERADA ===\n")

# VLANs
if "vlan" in prompt:

    vlans = {
        10: "ADMINISTRACION",
        20: "VENTAS",
        30: "SERVIDORES",
        40: "INVITADOS"
    }

    configs.append("! CONFIG VLANs\n")

    for numero, nombre in vlans.items():
        configs.append(f"vlan {numero}")
        configs.append(f" name {nombre}\n")

# DHCP
if "dhcp" in prompt:

    configs.append("! CONFIG DHCP\n")

    configs.append("ip dhcp pool ADMIN")
    configs.append(" network 192.168.10.0 255.255.255.0")
    configs.append(" default-router 192.168.10.1")
    configs.append(" dns-server 8.8.8.8\n")

# OSPF
if "ospf" in prompt:

    configs.append("! CONFIG OSPF\n")

    configs.append("router ospf 1")
    configs.append(" router-id 1.1.1.1")
    configs.append(" network 10.0.0.0 0.0.0.255 area 0\n")

# NAT
if "nat" in prompt:

    configs.append("! CONFIG NAT\n")

    configs.append("access-list 1 permit 192.168.0.0 0.0.255.255")
    configs.append("ip nat inside source list 1 interface g0/0 overload\n")

resultado = "\n".join(configs)

print("\n" + resultado)

with open("outputs/configs_generadas.txt", "w", encoding="utf-8") as archivo:
    archivo.write(resultado)

print("\nConfigs guardadas en outputs/configs_generadas.txt")