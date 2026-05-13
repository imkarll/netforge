from graphviz import Digraph

prompt = input("Describe la red: ").lower()

red = Digraph("NetForge")
red.attr(rankdir="LR")

# Nodos base
red.node("PC1", "PCs")
red.node("SW1", "Switch-Core")
red.node("R1", "Router-Core")

red.edge("PC1", "SW1")
red.edge("SW1", "R1")

# Internet
if "internet" in prompt or "isp" in prompt:
    red.node("ISP", "ISP")
    red.edge("R1", "ISP")

# Sucursal remota
if "remota" in prompt or "sucursal" in prompt:
    red.node("R2", "Router-Remoto")
    red.node("SW2", "Switch-Remoto")
    red.node("PC2", "PCs Remotos")

    if "internet" in prompt or "isp" in prompt:
        red.edge("ISP", "R2")
    else:
        red.edge("R1", "R2")

    red.edge("R2", "SW2")
    red.edge("SW2", "PC2")

# Servidores
if "servidor" in prompt:
    red.node("SRV", "Servidor")
    red.edge("SW1", "SRV")

# Guardar
red.render("outputs/topologia_dinamica", format="png", cleanup=True)

print("Topología dinámica generada.")