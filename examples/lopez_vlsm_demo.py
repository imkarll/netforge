from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from vlsm_calculator import calcular_vlsm, generar_texto_resultado


OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    necesidades_central = [
        {"nombre": "VLAN 20 Usuarios", "hosts": 80},
        {"nombre": "VLAN 10 CPD", "hosts": 20},
        {"nombre": "VLAN 30 IT", "hosts": 10},
        {"nombre": "VLAN 1 Administracion", "hosts": 6},
    ]

    necesidades_remota = [
        {"nombre": "VLAN 10 Fabrica", "hosts": 20},
        {"nombre": "VLAN 20 Distribucion", "hosts": 20},
        {"nombre": "VLAN 1 Administracion", "hosts": 6},
    ]

    necesidades_internet = [
        {"nombre": "Enlace I1-I2", "hosts": 2},
        {"nombre": "Enlace I2-I3", "hosts": 2},
        {"nombre": "Enlace I3-I4", "hosts": 2},
        {"nombre": "Enlace I4-I5", "hosts": 2},
        {"nombre": "Enlace I5-I6", "hosts": 2},
        {"nombre": "Enlace I6-I1", "hosts": 2},
        {"nombre": "PC Internet", "hosts": 2},
        {"nombre": "Servidor Web Publico", "hosts": 2},
    ]

    central = calcular_vlsm("192.168.1.0/24", necesidades_central)
    remota = calcular_vlsm("172.20.0.0/24", necesidades_remota)
    internet = calcular_vlsm("70.0.0.0/24", necesidades_internet)

    salida = []

    salida.append(generar_texto_resultado("OFICINA CENTRAL - VLSM", central))
    salida.append(generar_texto_resultado("OFICINA REMOTA - VLSM", remota))
    salida.append(generar_texto_resultado("INTERNET - VLSM", internet))

    contenido = "\n".join(salida)

    print(contenido)

    ruta = OUTPUT_DIR / "vlsm_plan_lopez_demo.txt"
    ruta.write_text(contenido, encoding="utf-8")

    print(f"\nPlan VLSM demo guardado en: {ruta}")


if __name__ == "__main__":
    main()