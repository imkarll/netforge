# NetForge

NetForge es una herramienta en Python para generar laboratorios básicos de redes tipo CCNA a partir de un enunciado en lenguaje natural.

El objetivo del proyecto es transformar una descripción como:

```text
Empresa con VLANs, DHCP, NAT, OSPF e ISP
```

en un conjunto de archivos listos para usar en Cisco Packet Tracer:

- configuraciones por dispositivo
- guía de pruebas
- resumen del laboratorio
- diagrama lógico de la topología

---

## Estado actual

Versión actual: `v0.1`

NetForge actualmente puede generar una topología base con:

- VLANs
- Router-on-a-stick
- DHCP por VLAN
- NAT overload
- enlace hacia ISP
- OSPF básico
- diagrama lógico en PNG
- documentación del laboratorio

---

## Estructura generada

Cada ejecución crea una carpeta nueva dentro de `outputs/`:

```text
outputs/lab_001/
├── SW1-CORE.txt
├── R1-CORE.txt
├── R-ISP.txt
├── GUIA_PRUEBAS.txt
├── RESUMEN_LAB.txt
└── topologia.png
```

---

## Topología recomendada

```text
PC1 Fa0       -> SW1 Fa0/1
SW1 Gi0/1     -> R1 Gi0/1
R1 Gi0/0      -> R-ISP Gi0/0
```

---

## Dispositivos usados en Packet Tracer

Recomendado:

- Router 2911 o 1941
- Switch 2960
- PCs genéricos

Importante: algunos routers usan interfaces distintas, por ejemplo:

```text
GigabitEthernet0/0
GigabitEthernet0/1
```

otros usan:

```text
GigabitEthernet0/0/0
GigabitEthernet0/0/1
```

Si el modelo del router usa nombres distintos, las configs deben adaptarse.

---

## Cómo ejecutar

Activar entorno virtual:

```bash
source venv/bin/activate
```

Ejecutar generador:

```bash
python3 multi_device_generator.py
```

Ejemplo de prompt:

```text
Empresa con VLANs, DHCP, NAT, OSPF e ISP
```

---

## Archivos generados

### `SW1-CORE.txt`

Configuración del switch:

- creación de VLANs
- puerto trunk hacia R1
- puertos access para PCs/servidores
- PortFast en puertos de acceso

### `R1-CORE.txt`

Configuración del router principal:

- subinterfaces router-on-a-stick
- gateways por VLAN
- DHCP pools
- NAT overload
- ruta por defecto hacia ISP
- OSPF básico

### `R-ISP.txt`

Configuración del router ISP simulado:

- enlace hacia R1
- ruta de retorno hacia redes internas
- OSPF opcional

### `GUIA_PRUEBAS.txt`

Comandos recomendados para verificar el laboratorio.

### `RESUMEN_LAB.txt`

Resumen del lab generado:

- enunciado original
- servicios detectados
- dispositivos generados
- VLANs
- topología recomendada
- archivos generados
- pruebas clave

### `topologia.png`

Diagrama visual generado automáticamente con Graphviz.

---

## Pruebas recomendadas en Packet Tracer

En SW1:

```cisco
show vlan brief
show interfaces trunk
```

En R1:

```cisco
show ip interface brief
show ip dhcp binding
show ip route
show ip nat translations
show ip ospf neighbor
```

Desde PC1:

```text
ping 192.168.10.1
ping 10.0.0.2
```

---

## Resultado probado

La versión actual fue probada en Packet Tracer con:

- PC conectado a VLAN 10
- Switch 2960
- Router-on-a-stick
- Router ISP simulado

Resultado:

- DHCP funcionó correctamente
- PC recibió IP `192.168.10.21`
- gateway `192.168.10.1`
- DNS `8.8.8.8`
- enlace R1 hacia ISP respondió ping

---

## Próximas mejoras

- Detectar cantidad de VLANs desde el prompt
- Permitir nombres personalizados de departamentos
- Generar direccionamiento dinámico
- Elegir interfaces según modelo de router
- Soportar múltiples sucursales
- Generar ACLs
- Generar configuración para servidores
- Exportar documentación en PDF
- Crear interfaz gráfica/web
- Integrar IA local para interpretar enunciados más complejos

---

## Objetivo final

Convertir NetForge en un copiloto educativo para redes:

```text
Enunciado de red
↓
Topología lógica
↓
Direccionamiento IP
↓
Configuraciones Cisco
↓
Diagrama visual
↓
Guía de pruebas
↓
Laboratorio funcional en Packet Tracer
```

NetForge no reemplaza aprender redes.  
NetForge ayuda a practicar, validar y acelerar laboratorios de redes.