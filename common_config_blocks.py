from netforge_settings import SSH_CONFIG


def generar_bloque_ssh():
    lineas = []

    lineas.append("! Configuracion SSH")
    lineas.append(f"ip domain-name {SSH_CONFIG['domain']}")
    lineas.append(f"username {SSH_CONFIG['user']} privilege 15 secret {SSH_CONFIG['secret']}")
    lineas.append(f"crypto key generate rsa modulus {SSH_CONFIG['rsa_modulus']}")
    lineas.append("ip ssh version 2")
    lineas.append("line vty 0 4")
    lineas.append(" login local")
    lineas.append(" transport input ssh")
    lineas.append("exit")
    lineas.append("")

    return lineas