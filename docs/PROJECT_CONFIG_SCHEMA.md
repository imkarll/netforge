# Project Config Schema

`project_config.json` será la fuente de verdad de cada proyecto creado con NetForge.

El objetivo de este archivo es guardar todos los parámetros necesarios para generar:

- direccionamiento
- topología
- configuraciones Cisco
- documentación
- pruebas

Los generadores no deberían depender de valores fijos dentro del código. Deben leer este archivo.

---

## Estructura general

```json
{
  "project_name": "Proyecto_NetForge",
  "mode": "basic",
  "global": {},
  "internet": {},
  "offices": [],
  "vpn": {},
  "management": {},
  "security": {},
  "services": {}
}
```

---

## Campos principales

### `project_name`

Nombre del proyecto.

```json
"project_name": "Lopez y Asociados"
```

### `mode`

Nivel o tipo del proyecto.

Valores posibles:

```text
basic
intermediate
advanced
final_project
```

Ejemplo:

```json
"mode": "advanced"
```

---

## Global

Configuraciones generales del proyecto.

```json
"global": {
  "gateway_policy": "last_usable",
  "dns_servers": ["8.8.8.8"],
  "use_vlsm": true,
  "default_subnet_for_p2p": 30
}
```

### `gateway_policy`

Define qué IP se usará como gateway en cada subred.

Valores posibles:

```text
first_usable
last_usable
manual
```

---

## Internet

Define si se simula una red de Internet/ISP.

```json
"internet": {
  "enabled": true,
  "routers": ["I1", "I2", "I3", "I4", "I5", "I6"],
  "base_network": "70.0.0.0/24",
  "topology": "ring",
  "routing_protocol": "ospf",
  "links": [],
  "edge_connections": []
}
```

### `topology`

Valores posibles:

```text
ring
line
full_mesh
custom
```

### `routing_protocol`

Valores posibles:

```text
ospf
static
rip
eigrp
none
```

### `edge_connections`

Conexiones entre Internet/ISP y routers de empresa.

```json
"edge_connections": [
  {
    "internet_router": "I1",
    "enterprise_router": "R1",
    "network": "80.0.0.0/24",
    "internet_ip": "80.0.0.2",
    "enterprise_ip": "80.0.0.1"
  },
  {
    "internet_router": "I4",
    "enterprise_router": "R2",
    "network": "90.0.0.0/24",
    "internet_ip": "90.0.0.1",
    "enterprise_ip": "90.0.0.2"
  }
]
```

---

## Offices

Lista de oficinas o sedes del proyecto.

```json
"offices": [
  {
    "name": "central",
    "base_network": "192.168.1.0/24",
    "inter_vlan_routing": "layer3_switch",
    "edge_router": "R1",
    "distribution_switch": "SW-DIST",
    "access_switches": ["SW1", "SW2", "SW3"],
    "vlans": [],
    "features": {},
    "links": {}
  }
]
```

### `inter_vlan_routing`

Valores posibles:

```text
layer3_switch
router_on_a_stick
none
```

---

## VLANs

Cada oficina puede tener varias VLANs.

```json
"vlans": [
  {
    "id": 10,
    "name": "CPD",
    "hosts": 20,
    "type": "servers"
  },
  {
    "id": 20,
    "name": "USUARIOS",
    "hosts": 80,
    "type": "users"
  },
  {
    "id": 30,
    "name": "IT",
    "hosts": 10,
    "type": "it"
  },
  {
    "id": 1,
    "name": "ADMINISTRACION",
    "hosts": 6,
    "type": "management"
  }
]
```

### `type`

Valores sugeridos:

```text
users
servers
management
guest
voice
it
factory
distribution
custom
```

---

## Features por oficina

```json
"features": {
  "dhcp": false,
  "nat": true,
  "ospf": true,
  "ssh": true,
  "syslog": true,
  "tftp_backup": true,
  "etherchannel": true,
  "port_security": true,
  "stp": false
}
```

---

## Switching

Configuración opcional para switches.

```json
"switching": {
  "native_vlan": 1,
  "allowed_vlans": [1, 10, 20, 30],
  "etherchannels": [
    {
      "from": "SW1",
      "to": "SW-DIST",
      "interfaces_from": ["fa0/23", "fa0/24"],
      "interfaces_to": ["fa0/1", "fa0/2"],
      "mode": "active",
      "port_channel": 1
    }
  ],
  "stp": {
    "enabled": true,
    "roots": [
      {
        "vlan": 10,
        "root": "SW4"
      },
      {
        "vlan": 20,
        "root": "SW5"
      }
    ]
  }
}
```

---

## Security

Configuraciones de seguridad.

```json
"security": {
  "port_security": {
    "enabled": true,
    "max_mac": 2,
    "violation": "shutdown",
    "sticky": true
  },
  "acls": [
    {
      "name": "BLOQUEAR_INVITADOS_SERVIDORES",
      "action": "deny",
      "protocol": "ip",
      "source": "VLAN40",
      "destination": "VLAN30",
      "apply_to": "g0/1.40",
      "direction": "in"
    }
  ]
}
```

---

## NAT

```json
"nat": {
  "enabled": true,
  "type": "pat",
  "inside_networks": ["192.168.1.0/24"],
  "outside_interface": "g0/0",
  "static_mappings": [
    {
      "description": "Publicar servidor web interno HTTP",
      "inside_ip": "192.168.1.129",
      "inside_port": 80,
      "outside_ip": "interface",
      "outside_port": 80,
      "protocol": "tcp"
    },
    {
      "description": "Publicar servidor web interno HTTPS",
      "inside_ip": "192.168.1.129",
      "inside_port": 443,
      "outside_ip": "interface",
      "outside_port": 443,
      "protocol": "tcp"
    }
  ]
}
```

---

## VPN

```json
"vpn": {
  "enabled": true,
  "type": "gre",
  "base_network": "172.16.0.0/16",
  "tunnels": [
    {
      "name": "Tunnel0",
      "source_router": "R1",
      "destination_router": "R2",
      "source_interface": "g0/0",
      "destination_public_ip": "90.0.0.2",
      "source_tunnel_ip": "172.16.0.1",
      "destination_tunnel_ip": "172.16.0.2",
      "mask": "255.255.255.252",
      "routing_protocol": "ospf"
    }
  ]
}
```

---

## Management

```json
"management": {
  "ssh": {
    "enabled": true,
    "domain": "netforge.local",
    "user": "admin",
    "secret": "Cisco123",
    "rsa_modulus": 1024
  },
  "syslog": {
    "enabled": true,
    "server_ip": "192.168.1.130",
    "trap_level": "warnings"
  },
  "tftp_backup": {
    "enabled": true,
    "server_ip": "192.168.1.131"
  },
  "ntp": {
    "enabled": false,
    "server_ip": null
  }
}
```

---

## Services

Servidores y servicios del proyecto.

```json
"services": {
  "servers": [
    {
      "name": "WEB-SERVER",
      "type": "web",
      "vlan": 10,
      "ip": "192.168.1.129",
      "services": ["http", "https"]
    },
    {
      "name": "SYSLOG-SERVER",
      "type": "syslog",
      "vlan": 10,
      "ip": "192.168.1.130",
      "services": ["syslog"]
    },
    {
      "name": "TFTP-SERVER",
      "type": "tftp",
      "vlan": 10,
      "ip": "192.168.1.131",
      "services": ["tftp"]
    }
  ]
}
```

---

## Objetivo del schema

Este schema debe permitir que NetForge genere proyectos distintos sin cambiar el código.

Los valores específicos de cada proyecto deben estar en `project_config.json`.

Los generadores deben leer este archivo y producir configs, documentación y pruebas basadas en esos datos.