from pathlib import Path

from requirements_parser import detectar_requisitos, generar_resumen
from vlsm_calculator import calcular_vlsm, generar_texto_resultado


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def construir_necesidades_vlsm(requisitos):
    necesidades = {
        "central": [],
        "remota": [],
        "internet": [],
    }

    for vlan in requisitos["oficina_central"]["vlans"]:
        necesidades["central"].append(
            {
                "nombre": f"VLAN {vlan['id']} {vlan['nombre']}",
                "hosts": vlan["hosts"] if isinstance(vlan["hosts"], int) else 6,
            }
        )

    for vlan in requisitos["oficina_remota"]["vlans"]:
        necesidades["remota"].append(
            {
                "nombre": f"VLAN {vlan['id']} {vlan['nombre']}",
                "hosts": vlan["hosts"] if isinstance(vlan["hosts"], int) else 6,
            }
        )

    routers_internet = requisitos["internet"]["routers"]

    if routers_internet:
        for indice in range(len(routers_internet)):
            origen = routers_internet[indice]
            destino = routers_internet[(indice + 1) % len(routers_internet)]

            necesidades["internet"].append(
                {
                    "nombre": f"Enlace {origen}-{destino}",
                    "hosts": 2,
                }
            )

    necesidades["internet"].append({"nombre": "PC Internet", "hosts": 2})
    necesidades["internet"].append({"nombre": "Servidor Web Publico", "hosts": 2})

    return necesidades


def generar_plan_maestro(texto_enunciado):
    requisitos = detectar_requisitos(texto_enunciado)
    resumen_requisitos = generar_resumen(requisitos)

    necesidades = construir_necesidades_vlsm(requisitos)

    plan_vlsm = []

    if requisitos["oficina_central"]["red_base"] and necesidades["central"]:
        central = calcular_vlsm(
            requisitos["oficina_central"]["red_base"],
            necesidades["central"],
        )
        plan_vlsm.append(generar_texto_resultado("OFICINA CENTRAL - VLSM", central))

    if requisitos["oficina_remota"]["red_base"] and necesidades["remota"]:
        remota = calcular_vlsm(
            requisitos["oficina_remota"]["red_base"],
            necesidades["remota"],
        )
        plan_vlsm.append(generar_texto_resultado("OFICINA REMOTA - VLSM", remota))

    if requisitos["internet"]["red_base"] and necesidades["internet"]:
        internet = calcular_vlsm(
            requisitos["internet"]["red_base"],
            necesidades["internet"],
        )
        plan_vlsm.append(generar_texto_resultado("INTERNET - VLSM", internet))

    lineas = []

    lineas.append("=== NETFORGE: PLAN MAESTRO DEL PROYECTO ===\n")

    lineas.append("## 1. Requisitos detectados\n")
    lineas.append(resumen_requisitos)
    lineas.append("\n")

    lineas.append("## 2. Plan de direccionamiento VLSM\n")

    if plan_vlsm:
        lineas.append("\n".join(plan_vlsm))
    else:
        lineas.append("No se pudo generar plan VLSM porque faltan redes base o necesidades.")

    lineas.append("\n")

    lineas.append("## 3. Orden recomendado de implementación\n")
    lineas.append("1. Calcular y validar direccionamiento VLSM")
    lineas.append("2. Crear topología física en Packet Tracer")
    lineas.append("3. Configurar routers de Internet I1-I6")
    lineas.append("4. Configurar OSPF en la red de Internet")
    lineas.append("5. Configurar oficina central")
    lineas.append("6. Configurar oficina remota")
    lineas.append("7. Configurar NAT/PAT en R1 y R2")
    lineas.append("8. Configurar GRE VPN entre oficinas")
    lineas.append("9. Configurar SSH, Syslog y backups TFTP")
    lineas.append("10. Ejecutar checklist de pruebas")
    lineas.append("")

    lineas.append("## 4. Próximos módulos necesarios\n")
    lineas.append("- Generador de configuración para routers de Internet")
    lineas.append("- Generador de configuración para switch L3 central")
    lineas.append("- Generador de configuración para switches de acceso")
    lineas.append("- Generador de configuración para R1/R2 NAT/PAT")
    lineas.append("- Generador de configuración GRE VPN")
    lineas.append("- Generador de configuración SSH/Syslog/TFTP")
    lineas.append("")

    return "\n".join(lineas)


def main():
    print("Pega el enunciado completo. Cuando termines, escribe una línea con solo FIN:\n")

    lineas = []

    while True:
        linea = input()

        if linea.strip().upper() == "FIN":
            break

        lineas.append(linea)

    texto_enunciado = "\n".join(lineas)

    plan_maestro = generar_plan_maestro(texto_enunciado)

    print("\n" + plan_maestro)

    ruta = OUTPUT_DIR / "plan_maestro.txt"
    ruta.write_text(plan_maestro, encoding="utf-8")

    print(f"\nPlan maestro guardado en: {ruta}")


if __name__ == "__main__":
    main()