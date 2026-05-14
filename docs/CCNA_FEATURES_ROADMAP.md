# CCNA Features Roadmap

Este documento define las funciones CCNA que NetForge debería soportar progresivamente.

El objetivo no es implementar todo de golpe, sino ordenar las funciones por fases para que el proyecto crezca sin convertirse en spaghetti.

---

## Fase 1 — Core básico configurable

Objetivo: permitir crear proyectos simples desde parámetros del usuario.

### Funciones

- Crear proyecto desde asistente guiado
- Generar `project_config.json`
- Leer `project_config.json`
- Calcular VLSM
- Generar plan de direccionamiento
- Generar resumen del proyecto
- Generar estructura de carpetas por proyecto

### Redes soportadas

- Una oficina
- Varias VLANs
- Red base configurable
- Gateway configurable:
  - primera IP útil
  - última IP útil
  - manual

### Configuración Cisco básica

- VLANs
- Puertos access
- Trunks
- Router-on-a-stick
- Switch capa 3 con SVIs
- Ruta por defecto
- DHCP básico
- NAT/PAT básico
- SSH básico

---

## Fase 2 — Switching CCNA

Objetivo: cubrir la parte de switching de CCNA.

### VLANs

- Crear VLANs
- Nombrar VLANs
- VLAN de administración
- VLAN nativa
- VLAN de invitados
- VLAN de servidores
- VLAN de voz

### Trunks

- `switchport mode trunk`
- VLANs permitidas
- VLAN nativa
- Verificación con `show interfaces trunk`

### EtherChannel

- LACP active/passive
- PAgP desirable/auto
- Mode on
- Port-channel
- Trunks sobre EtherChannel
- Verificación con:
  - `show etherchannel summary`
  - `show interfaces port-channel`

### STP

- STP por defecto
- Root bridge por VLAN
- Root primary/secondary
- PortFast
- BPDU Guard
- Verificación con:
  - `show spanning-tree`
  - `show spanning-tree vlan X`

---

## Fase 3 — Routing CCNA

Objetivo: generar configuraciones de routing para redes LAN, WAN y multi-sede.

### Routing estático

- Rutas estáticas
- Rutas por defecto
- Rutas flotantes
- Rutas de retorno

### OSPF

- OSPFv2 single-area
- Router ID
- Network statements
- Wildcard masks
- Passive interfaces
- Default route advertisement
- OSPF entre sedes
- OSPF sobre túnel GRE
- Verificación con:
  - `show ip ospf neighbor`
  - `show ip route ospf`
  - `show ip protocols`

### Otros protocolos posibles

- RIP
- EIGRP

Estos quedan como roadmap, no prioridad inicial.

---

## Fase 4 — Servicios de red

Objetivo: soportar servicios comunes en proyectos Packet Tracer/CCNA.

### DHCP

- DHCP pools por VLAN
- Excluded addresses
- Default gateway
- DNS
- Domain name
- DHCP relay helper-address

### DNS

- Servidor DNS documentado
- Registros básicos
- Pruebas de resolución

### Web

- Servidor HTTP
- Servidor HTTPS
- Publicación mediante NAT estático

### Syslog

- `logging host`
- `logging trap`
- timestamps
- servidor Syslog documentado

### TFTP

- servidor TFTP documentado
- comandos de backup:
  - `copy running-config startup-config`
  - `copy running-config tftp`

### NTP

- servidor NTP
- `ntp server`
- timestamps sincronizados

---

## Fase 5 — Seguridad CCNA

Objetivo: añadir configuraciones de seguridad habituales en CCNA.

### SSH

- Dominio
- Usuario local
- Secret
- RSA keys
- SSH version 2
- VTY lines
- Deshabilitar Telnet
- Verificación con:
  - `show ip ssh`
  - `show users`
  - prueba SSH desde PC

### Port Security

- Activar port-security
- Maximum MAC
- Violation mode:
  - shutdown
  - restrict
  - protect
- MAC sticky
- Verificación con:
  - `show port-security`
  - `show port-security interface`

### ACLs

- ACL estándar
- ACL extendida
- ACL nombrada
- Filtrado por:
  - origen
  - destino
  - protocolo
  - puerto
- Aplicación inbound/outbound
- Casos comunes:
  - invitados no acceden a servidores
  - solo IT puede hacer SSH
  - bloquear tráfico entre VLANs
  - permitir HTTP/HTTPS hacia servidor web

---

## Fase 6 — NAT/PAT

Objetivo: soportar salida a Internet y publicación de servicios.

### PAT overload

- NAT inside
- NAT outside
- ACL de redes internas
- Overload sobre interfaz externa

### NAT estático

- Publicar servidor interno
- Publicar HTTP
- Publicar HTTPS
- Publicar SSH si el proyecto lo pide

### Verificación

- `show ip nat translations`
- `show ip nat statistics`
- ping hacia ISP
- prueba web desde Internet hacia servidor interno

---

## Fase 7 — VPN y multi-sede

Objetivo: soportar proyectos con varias sedes conectadas por Internet.

### GRE

- Tunnel interfaces
- Tunnel source
- Tunnel destination
- IP del túnel
- Routing por túnel

### OSPF sobre GRE

- Publicar redes LAN de cada sede
- No publicar redes privadas directamente en Internet
- Verificar vecinos OSPF por túnel

### Futuro

- IPsec
- GRE over IPsec

---

## Fase 8 — Topología y documentación

Objetivo: generar material presentable para proyectos.

### Topología lógica

- Diagrama PNG
- Routers
- Switches
- VLANs
- Enlaces
- Redes
- Direcciones IP principales

### Documentación final

- Resumen del proyecto
- Requisitos detectados
- Plan VLSM
- Tabla de VLANs
- Tabla de dispositivos
- Tabla de direccionamiento
- Configuraciones por dispositivo
- Guía de pruebas
- Conclusiones

### Formatos

- Markdown
- TXT
- PDF en el futuro

---

## Fase 9 — Validación

Objetivo: detectar errores antes de generar configs.

### Validaciones necesarias

- VLAN IDs duplicados
- Redes superpuestas
- Hosts insuficientes para una subred
- IPs duplicadas
- Gateway fuera de red
- Trunks sin VLANs permitidas
- NAT sin inside/outside
- OSPF sin redes publicadas
- GRE sin IP pública de destino
- SSH sin usuario
- Syslog/TFTP sin servidor definido

### Salidas

- Errores críticos
- Advertencias
- Recomendaciones

---

## Fase 10 — Experiencia de usuario

Objetivo: que NetForge sea cómodo para estudiantes.

### Modos

- Modo básico
- Modo intermedio
- Modo avanzado
- Modo proyecto final
- Modo desde enunciado

### Interfaz

Primero:

- CLI interactiva

Después:

- menú textual
- carga de JSON
- posible interfaz web

### Plantillas

- LAN básica
- Router-on-a-stick
- Switch capa 3
- NAT + Internet
- OSPF multi-router
- GRE VPN
- Proyecto final completo

---

## Prioridad inmediata

La prioridad actual de NetForge es:

1. Definir `project_config.json`
2. Crear `project_wizard.py`
3. Hacer que `project_solver.py` lea `project_config.json`
4. Generar VLSM desde JSON
5. Convertir generadores actuales en módulos genéricos
6. Usar López y Asociados como plantilla avanzada, no como lógica hardcodeada

---

## Regla de arquitectura

Todo valor específico de un proyecto debe vivir en:

```text
project_config.json
```

o en archivos dentro de:

```text
examples/
```

Los módulos reutilizables no deben tener valores fijos de un proyecto concreto.