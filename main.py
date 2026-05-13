prompt = input("Describe la red: ")
texto = prompt.lower()

lineas = []

lineas.append("=== NetForge: Topología generada ===\n")

dispositivos = ["R1-Core", "SW1-Core"]

if "remota" in texto or "sucursal" in texto:
    dispositivos += ["R2-Remota", "SW2-Remota"]

if "isp" in texto or "internet" in texto:
    dispositivos.append("R-ISP")

lineas.append("Dispositivos sugeridos:")
for d in dispositivos:
    lineas.append(f"- {d}")

lineas.append("\nServicios detectados:")
servicios_detectados = []

for servicio in ["vlan", "ospf", "dhcp", "nat"]:
    if servicio in texto:
        servicios_detectados.append(servicio.upper())
        lineas.append(f"- {servicio.upper()}")

if not servicios_detectados:
    lineas.append("- Ningún servicio específico detectado")

lineas.append("\nTopología lógica:")
if "remota" in texto or "sucursal" in texto:
    lineas.append("PCs Central -> SW1-Core -> R1-Core -> R-ISP -> R2-Remota -> SW2-Remota -> PCs Remota")
else:
    lineas.append("PCs -> SW1-Core -> R1-Core -> Internet")

lineas.append("\nVLANs sugeridas:")
vlans = {
    10: "Administracion",
    20: "Ventas",
    30: "Servidores",
    40: "Invitados"
}

for numero, nombre in vlans.items():
    lineas.append(f"VLAN {numero}: {nombre}")

lineas.append("\nComandos Cisco base para switch:")
for numero, nombre in vlans.items():
    lineas.append(f"vlan {numero}")
    lineas.append(f" name {nombre}")

lineas.append("\nChecklist de pruebas:")
lineas.append("- Hacer ping entre PCs de la misma VLAN")
lineas.append("- Probar DHCP en clientes")
lineas.append("- Verificar OSPF con: show ip ospf neighbor")
lineas.append("- Verificar NAT con: show ip nat translations")

resultado = "\n".join(lineas)

print("\n" + resultado)

with open("outputs/topologia_generada.txt", "w", encoding="utf-8") as archivo:
    archivo.write(resultado)

print("\nArchivo guardado en: outputs/topologia_generada.txt")