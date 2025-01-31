#!/usr/bin/env python3

import os
import click
import subprocess

print()
print("-----------------------------------")
print("--- Crear una red de OpenNebula ---")
print("-----------------------------------")
print()

nombre = click.prompt("Nombre de la red", default="test")
subred = click.prompt("Subred", default="172.20.227.0")
mascara = click.prompt("Máscara", default="255.255.0.0")
gateway = click.prompt("Puerta de enlace", default="172.20.1.2")
dns = click.prompt("Servidores de nombres", default="192.168.10.1 1.1.1.1")
privadas = click.prompt("Direcciones", default=10)
inicial_privadas = click.prompt("Número de host inicial para las direcciones privadas", default=10)

print()

try:
    print(f"Creando la red {nombre}...")
    f = open("temp.txt", "w")
    f.write(f"NAME = \"{nombre}\"" + "\n")
    f.write("BRIDGE = \"aulas\"" + "\n")
    f.write("BRIDGE_TYPE = \"linux\"" + "\n")
    f.write(f"DNS = \"{dns}\"" + "\n")
    f.write(f"GATEWAY = \"{gateway}\"" + "\n")
    f.write(f"NETWORK_MASK = \"{mascara}\"" + "\n")
    f.write("OUTER_VLAN_ID = \"\"" + "\n")
    f.write("PHYDEV = \"\"" + "\n")
    f.write("SECURITY_GROUPS = \"0\"" + "\n")
    f.write("VLAN_ID = \"\"" + "\n")
    f.write("VN_MAD = \"fw\"" + "\n")
    f.write("AR=[TYPE = \"IP4\", IP = \""
            + subred[:-1] + str(inicial_privadas) + "\", SIZE = \""
            + str(privadas) + "\" ]" + "\n")
    f.close()
    vnet_id = subprocess.run(['onevnet', 'create', 'temp.txt'],
                             capture_output=True, text=True).stdout.split()[-1]
    print(f"ID: {vnet_id}")
    os.remove("temp.txt")

except:
    print("Error al crear la red.")
