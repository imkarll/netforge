def generar_bloque_ssh(ssh_config):
    if not ssh_config.get("enabled", False):
        return []

    domain = ssh_config.get("domain", "netforge.local")
    user = ssh_config.get("user", "admin")
    secret = ssh_config.get("secret", "Cisco123")
    rsa_modulus = ssh_config.get("rsa_modulus", 1024)

    lineas = []

    lineas.append("! Configuracion SSH")
    lineas.append(f"ip domain-name {domain}")
    lineas.append(f"username {user} privilege 15 secret {secret}")
    lineas.append(f"crypto key generate rsa modulus {rsa_modulus}")
    lineas.append("ip ssh version 2")
    lineas.append("line vty 0 4")
    lineas.append(" login local")
    lineas.append(" transport input ssh")
    lineas.append("exit")
    lineas.append("")

    return lineas