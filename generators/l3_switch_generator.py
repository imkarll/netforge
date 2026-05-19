from pathlib import Path

from common_config_blocks import generar_bloque_ssh
from vlsm_from_config import calcular_vlsm_oficina


def generar_config_l3_switch(office, vlsm_plan, management_config, gateway_policy):
    switch_name = office.get("distribution_switch") or "SW-DIST"

    lineas = []

    lineas.append("enable")
    lineas.append("configure terminal")
    lineas.append(f"hostname {switch_name}")
    lineas.append("")

    if management_config.get("ssh", {}).get("enabled"):
        lineas.extend(generar_bloque_ssh(management_config.get("ssh", {})))

    lineas.append("! Habilitar routing capa 3")
    lineas.append("ip routing")
    lineas.append("")

    lineas.append("! Crear VLANs")
    for item in vlsm_plan:
        lineas.append(f"vlan {item['vlan_id']}")
        lineas.append(f" name {item['vlan_name']}")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! Interfaces VLAN / Gateways")
    for item in vlsm_plan:
        lineas.append(f"interface vlan {item['vlan_id']}")
        lineas.append(f" description GATEWAY-{item['vlan_name']}")
        lineas.append(f" ip address {item['gateway']} {item['mask']}")
        lineas.append(" no shutdown")
        lineas.append("exit")
        lineas.append("")

    lineas.append("! OSPF si aplica")
    if office["features"].get("ospf"):
        lineas.append("router ospf 1")
        lineas.append(" router-id 10.10.10.10")

        for item in vlsm_plan:
            lineas.append(f" network {item['network']} {item['wildcard']} area 0")

        lineas.append(" passive-interface default")
        lineas.append("")

    else:
        lineas.append("! OSPF no habilitado para esta oficina")
        lineas.append("")

    lineas.append("end")
    lineas.append("write memory")

    return "\n".join(lineas)


def generar_l3_switches_desde_config(config, output_base_dir):
    gateway_policy = config["global"].get("gateway_policy", "last_usable")
    management_config = config.get("management", {})

    output_dir = Path(output_base_dir) / "configs" / "switches"
    output_dir.mkdir(parents=True, exist_ok=True)

    archivos_generados = []

    for office in config["offices"]:
        if office["inter_vlan_routing"] != "layer3_switch":
            continue

        vlsm_plan = calcular_vlsm_oficina(office, gateway_policy)

        config_text = generar_config_l3_switch(
            office=office,
            vlsm_plan=vlsm_plan,
            management_config=management_config,
            gateway_policy=gateway_policy,
        )

        switch_name = office.get("distribution_switch") or "SW-DIST"
        ruta = output_dir / f"{switch_name}.txt"
        ruta.write_text(config_text, encoding="utf-8")

        archivos_generados.append(ruta)

    return archivos_generados