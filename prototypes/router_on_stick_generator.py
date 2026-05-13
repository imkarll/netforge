prompt = input("Describe la red: ").lower()

usa_nat = "nat" in prompt
usa_ospf = "ospf" in prompt
usa_dhcp = "dhcp" in prompt
usa_isp = "isp" in prompt or "internet" in prompt

vlans = {
    10: {
        "nombre": "ADMINISTRACION",
        "red": "192.168.10.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.10.1"
    },
    20: {
        "nombre": "VENTAS",
        "red": "192.168.20.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.20.1"
    },
    30: {
        "nombre": "SERVIDORES",
        "red": "192.168.30.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.30.1"
    },
    40: {
        "nombre": "INVITADOS",
        "red": "192.168.40.0",
        "mascara": "255.255.255.0",
        "gateway": "192.168.40.1"
    }
}

lineas = []

lineas.append("=== NETFORGE: ROUTER-ON-A-STICK ===\n")

# =========================
# SWITCH
# =========================

lineas.append("=== SW1-CORE ===")
lineas.append("enable")
lineas.append("configure terminal")
lineas.append("hostname SW1-CORE\n")

lineas.append("! Crear VLANs")
for vlan_id, datos in vlans.items():
    lineas.append(f"vlan {vlan_id}")
    lineas.append(f" name {datos['nombre']}")
lineas.append("")

lineas.append("! Puerto trunk hacia el router")
lineas.append("interface g0/1")
lineas.append(" description TRUNK-HACIA-R1-CORE")
lineas.append(" switchport mode trunk")
lineas.append(" switchport trunk allowed vlan 10,20,30,40")
lineas.append(" no shutdown")
lineas.append("exit\n")

lineas.append("! Puertos de acceso ejemplo")
lineas.append("interface f0/1")
lineas.append(" description PC-ADMINISTRACION")
lineas.append(" switchport mode access")
lineas.append(" switchport access vlan 10")
lineas.append(" spanning-tree portfast")
lineas.append("exit\n")

lineas.append("interface f0/2")
lineas.append(" description PC-VENTAS")
lineas.append(" switchport mode access")
lineas.append(" switchport access vlan 20")
lineas.append(" spanning-tree portfast")
lineas.append("exit\n")

lineas.append("interface f0/3")
lineas.append(" description SERVIDOR")
lineas.append(" switchport mode access")
lineas.append(" switchport access vlan 30")
lineas.append(" spanning-tree portfast")
lineas.append("exit\n")

lineas.append("interface f0/4")
lineas.append(" description PC-INVITADOS")
lineas.append(" switchport mode access")
lineas.append(" switchport access vlan 40")
lineas.append(" spanning-tree portfast")
lineas.append("exit\n")

lineas.append("end")
lineas.append("write memory\n")

# =========================
# ROUTER
# =========================

lineas.append("=== R1-CORE ===")
lineas.append("enable")
lineas.append("configure terminal")
lineas.append("hostname R1-CORE\n")

lineas.append("! Interfaz física hacia switch")
lineas.append("interface g0/1")
lineas.append(" description TRUNK-HACIA-SW1-CORE")
lineas.append(" no shutdown")
lineas.append("exit\n")

lineas.append("! Subinterfaces Router-on-a-Stick")
for vlan_id, datos in vlans.items():
    lineas.append(f"interface g0/1.{vlan_id}")
    lineas.append(f" description GATEWAY-{datos['nombre']}")
    lineas.append(f" encapsulation dot1Q {vlan_id}")
    lineas.append(f" ip address {datos['gateway']} {datos['mascara']}")
    if usa_nat:
        lineas.append(" ip nat inside")
    lineas.append("exit\n")

if usa_dhcp:
    lineas.append("! Excluir gateways del DHCP")
    for vlan_id, datos in vlans.items():
        gateway = datos["gateway"]
        base = gateway.rsplit(".", 1)[0]
        lineas.append(f"ip dhcp excluded-address {base}.1 {base}.20")
    lineas.append("")

    lineas.append("! DHCP Pools")
    for vlan_id, datos in vlans.items():
        lineas.append(f"ip dhcp pool {datos['nombre']}")
        lineas.append(f" network {datos['red']} {datos['mascara']}")
        lineas.append(f" default-router {datos['gateway']}")
        lineas.append(" dns-server 8.8.8.8")
        lineas.append("")

if usa_isp or usa_nat:
    lineas.append("! Enlace hacia ISP / Internet")
    lineas.append("interface g0/0")
    lineas.append(" description HACIA-ISP")
    lineas.append(" ip address 10.0.0.1 255.255.255.252")
    if usa_nat:
        lineas.append(" ip nat outside")
    lineas.append(" no shutdown")
    lineas.append("exit\n")

    lineas.append("! Ruta por defecto hacia ISP")
    lineas.append("ip route 0.0.0.0 0.0.0.0 10.0.0.2\n")

if usa_nat:
    lineas.append("! NAT Overload")
    lineas.append("access-list 1 permit 192.168.0.0 0.0.255.255")
    lineas.append("ip nat inside source list 1 interface g0/0 overload\n")

if usa_ospf:
    lineas.append("! OSPF")
    lineas.append("router ospf 1")
    lineas.append(" router-id 1.1.1.1")
    lineas.append(" network 192.168.0.0 0.0.255.255 area 0")
    lineas.append(" network 10.0.0.0 0.0.0.3 area 0")
    lineas.append(" passive-interface g0/1.10")
    lineas.append(" passive-interface g0/1.20")
    lineas.append(" passive-interface g0/1.30")
    lineas.append(" passive-interface g0/1.40")
    lineas.append(" no passive-interface g0/0")
    lineas.append("")

lineas.append("end")
lineas.append("write memory\n")

# =========================
# ISP
# =========================

if usa_isp:
    lineas.append("=== R-ISP ===")
    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append("hostname R-ISP\n")

    lineas.append("interface g0/0")
    lineas.append(" description HACIA-R1-CORE")
    lineas.append(" ip address 10.0.0.2 255.255.255.252")
    lineas.append(" no shutdown")
    lineas.append("exit\n")

    lineas.append("! Ruta de retorno hacia redes internas")
    lineas.append("ip route 192.168.0.0 255.255.0.0 10.0.0.1\n")

    lineas.append("end")
    lineas.append("write memory\n")

# =========================
# TABLA IP
# =========================

lineas.append("=== TABLA DE DIRECCIONAMIENTO ===")
lineas.append("Dispositivo/Interfaz        IP                  Máscara")
lineas.append("R1 g0/1.10                  192.168.10.1        255.255.255.0")
lineas.append("R1 g0/1.20                  192.168.20.1        255.255.255.0")
lineas.append("R1 g0/1.30                  192.168.30.1        255.255.255.0")
lineas.append("R1 g0/1.40                  192.168.40.1        255.255.255.0")

if usa_isp or usa_nat:
    lineas.append("R1 g0/0                     10.0.0.1            255.255.255.252")
    lineas.append("R-ISP g0/0                  10.0.0.2            255.255.255.252")

lineas.append("")

# =========================
# CHECKLIST
# =========================

lineas.append("=== CHECKLIST DE PRUEBAS ===")
lineas.append("1. En SW1: show vlan brief")
lineas.append("2. En SW1: show interfaces trunk")
lineas.append("3. En R1: show ip interface brief")
lineas.append("4. En PCs: verificar que reciban IP por DHCP")
lineas.append("5. Ping desde PC VLAN 10 hacia 192.168.20.1")
lineas.append("6. Ping desde PC VLAN 10 hacia 10.0.0.2")
lineas.append("7. Si hay NAT: show ip nat translations")
lineas.append("8. Si hay OSPF: show ip ospf neighbor")

resultado = "\n".join(lineas)

print("\n" + resultado)

with open("outputs/router_on_stick_config.txt", "w", encoding="utf-8") as archivo:
    archivo.write(resultado)

print("\nConfig guardada en outputs/router_on_stick_config.txt")