prompt = input("Describe la red: ").lower()

configs = []

configs.append("=== NETFORGE: CONFIGURACIÓN POR DISPOSITIVO ===\n")

# Detectores
usa_vlans = "vlan" in prompt
usa_dhcp = "dhcp" in prompt
usa_ospf = "ospf" in prompt
usa_nat = "nat" in prompt
usa_remota = "remota" in prompt or "sucursal" in prompt
usa_isp = "isp" in prompt or "internet" in prompt

vlans = {
    10: ("ADMINISTRACION", "192.168.10.0", "255.255.255.0", "192.168.10.1"),
    20: ("VENTAS", "192.168.20.0", "255.255.255.0", "192.168.20.1"),
    30: ("SERVIDORES", "192.168.30.0", "255.255.255.0", "192.168.30.1"),
    40: ("INVITADOS", "192.168.40.0", "255.255.255.0", "192.168.40.1"),
}

# SWITCH CORE
configs.append("=== SW1-CORE ===")
configs.append("enable")
configs.append("configure terminal")
configs.append("hostname SW1-CORE\n")

if usa_vlans:
    configs.append("! VLANs")
    for numero, datos in vlans.items():
        nombre = datos[0]
        configs.append(f"vlan {numero}")
        configs.append(f" name {nombre}")
    configs.append("")

configs.append("end")
configs.append("write memory\n")

# ROUTER CORE
configs.append("=== R1-CORE ===")
configs.append("enable")
configs.append("configure terminal")
configs.append("hostname R1-CORE\n")

if usa_dhcp:
    configs.append("! DHCP Pools")
    for numero, datos in vlans.items():
        nombre, red, mascara, gateway = datos
        configs.append(f"ip dhcp pool {nombre}")
        configs.append(f" network {red} {mascara}")
        configs.append(f" default-router {gateway}")
        configs.append(" dns-server 8.8.8.8")
        configs.append("")

if usa_ospf:
    configs.append("! OSPF")
    configs.append("router ospf 1")
    configs.append(" router-id 1.1.1.1")
    configs.append(" network 192.168.0.0 0.0.255.255 area 0")
    configs.append(" network 10.0.0.0 0.0.0.255 area 0\n")

if usa_nat:
    configs.append("! NAT")
    configs.append("access-list 1 permit 192.168.0.0 0.0.255.255")
    configs.append("interface g0/0")
    configs.append(" ip nat outside")
    configs.append("exit")
    configs.append("interface g0/1")
    configs.append(" ip nat inside")
    configs.append("exit")
    configs.append("ip nat inside source list 1 interface g0/0 overload\n")

configs.append("end")
configs.append("write memory\n")

# ROUTER REMOTO
if usa_remota:
    configs.append("=== R2-REMOTA ===")
    configs.append("enable")
    configs.append("configure terminal")
    configs.append("hostname R2-REMOTA\n")

    if usa_ospf:
        configs.append("! OSPF remoto")
        configs.append("router ospf 1")
        configs.append(" router-id 2.2.2.2")
        configs.append(" network 192.168.50.0 0.0.0.255 area 0")
        configs.append(" network 10.0.0.0 0.0.0.255 area 0\n")

    configs.append("end")
    configs.append("write memory\n")

# ISP
if usa_isp:
    configs.append("=== R-ISP ===")
    configs.append("enable")
    configs.append("configure terminal")
    configs.append("hostname R-ISP\n")
    configs.append("! Config básica ISP simulada")
    configs.append("interface g0/0")
    configs.append(" description Enlace hacia R1-CORE")
    configs.append(" no shutdown")
    configs.append("exit")
    configs.append("interface g0/1")
    configs.append(" description Enlace hacia R2-REMOTA o Internet simulado")
    configs.append(" no shutdown")
    configs.append("exit\n")
    configs.append("end")
    configs.append("write memory\n")

resultado = "\n".join(configs)

print("\n" + resultado)

with open("outputs/configs_por_dispositivo.txt", "w", encoding="utf-8") as archivo:
    archivo.write(resultado)

print("\nConfigs guardadas en outputs/configs_por_dispositivo.txt")