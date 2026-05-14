# NetForge

NetForge es una herramienta en Python para generar proyectos de red Cisco/Packet Tracer a partir de requisitos definidos por el usuario.

El objetivo es que el usuario pueda introducir un enunciado o responder a un asistente guiado, y que NetForge genere:

- análisis de requisitos
- plan de direccionamiento IP
- cálculo VLSM
- topología lógica
- configuraciones Cisco por dispositivo
- guías de prueba
- documentación final del proyecto

## Objetivo principal

NetForge debe ser una herramienta general para proyectos CCNA, no un programa específico para un único enunciado.

El proyecto de "López y Asociados" será usado como caso de prueba avanzado, pero la arquitectura debe permitir crear otros proyectos con diferentes:

- redes base
- cantidad de oficinas
- cantidad de routers
- cantidad de switches
- VLANs
- hosts por VLAN
- tecnologías requeridas
- protocolos de routing
- servicios de red
- requisitos de seguridad

## Flujo ideal

```text
Entrada del usuario
↓
Project Wizard o parser de enunciado
↓
project_config.json
↓
Project Solver
↓
VLSM calculator
↓
Generadores Cisco
↓
Outputs finales
Modos de uso

NetForge debería soportar varios modos:

Proyecto desde asistente guiado
Proyecto desde enunciado largo
Proyecto desde archivo JSON existente
Plantilla de laboratorio simple
Plantilla de proyecto avanzado
Principio de diseño

Los generadores no deben tener valores fijos hardcodeados salvo en ejemplos o demos.

Todo proyecto real debe generarse desde un archivo:

project_config.json

Ese archivo será la fuente de verdad del proyecto.

Salida esperada

Cada proyecto debe generar una carpeta propia:

outputs/<nombre_proyecto>/
├── project_config.json
├── 01_requisitos_detectados.txt
├── 02_plan_vlsm.txt
├── 03_topologia_logica.png
├── 04_plan_implementacion.txt
├── configs/
│   ├── routers/
│   ├── switches/
│   └── servers/
├── pruebas/
│   ├── checklist_general.txt
│   ├── pruebas_vlan.txt
│   ├── pruebas_ospf.txt
│   ├── pruebas_nat.txt
│   ├── pruebas_vpn.txt
│   └── pruebas_ssh.txt
└── documentacion_final.md

Filosofía

NetForge no debe reemplazar el aprendizaje de redes.

Debe ayudar a:

organizar requisitos
evitar errores de cálculo
acelerar configuraciones repetitivas
generar documentación limpia
validar proyectos CCNA