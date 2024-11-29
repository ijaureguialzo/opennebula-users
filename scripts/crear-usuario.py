#!/usr/bin/env python3

import os
import click
import subprocess

print()
print("-------------------------------------------------")
print("--- Crear un usuario individual de OpenNebula ---")
print("-------------------------------------------------")
print()

print("--- Datos del usuario --------------")
nombre = click.prompt("Nombre de usuario", default="test")
separador = click.prompt("Separador", default="-")
numero = click.prompt("Número de usuario", default=1)
contrasenya = click.prompt("Contraseña", hide_input=True, confirmation_prompt="Confirmar contraseña")
grupo = click.prompt("Grupo de usuarios", default=nombre)

print("--- Cuota de recursos --------------")
cpus = click.prompt("CPUs", type=float, default=4)
ram = click.prompt("RAM (GiB)", type=float, default=12)
disco = click.prompt("Disco (GiB)", type=float, default=64)

print("--- Red del usuario ----------------")
subred = click.prompt("Subred", default="172.20.227.0")
mascara = click.prompt("Máscara", default="255.255.0.0")
gateway = click.prompt("Puerta de enlace", default="172.20.1.2")
dns = click.prompt("Servidores de nombres", default="192.168.10.1 1.1.1.1")
publicas = click.prompt("Direcciones públicas", default=0)
if publicas > 0:
    inicial_publicas = click.prompt("Número de host inicial para las direcciones públicas", default=1)
else:
    inicial_publicas = 0
privadas = click.prompt("Direcciones privadas", default=10)
if publicas > 0:
    inicial_privadas = click.prompt("Número de host inicial para las direcciones privadas", default=50)
else:
    inicial_privadas = click.prompt("Número de host inicial para las direcciones privadas", default=10)

print()

print(f"Creando el grupo {grupo}...")
os.system("onegroup create " + grupo)
os.system("onevdc delgroup default " + grupo)

usuario = nombre + separador + "{0:0>2}".format(numero)

print(f"\nCreando el usuario {usuario} y sus recursos asociados...\n")

print(f"Creando el datacenter {usuario}...")
os.system("onevdc create " + usuario)

print(f"Creando el grupo {usuario}...")
os.system("onegroup create " + usuario)

f = open("temp.txt", "w")
f.write("SUNSTONE=[")
f.write("DEFAULT_VIEW=\"user\", GROUP_ADMIN_DEFAULT_VIEW=\"groupadmin\", ")
f.write("GROUP_ADMIN_VIEWS=\"groupadmin\", VIEWS=\"cloud,user\"")
f.write("]")
f.close()
os.system("onegroup update " + usuario + " temp.txt")
os.remove("temp.txt")

os.system("onevdc addgroup " + usuario + " " + usuario)
os.system("onevdc delgroup default " + usuario)
os.system("onevdc addhost " + usuario + " 0 localhost")
os.system("onevdc adddatastore " + usuario + " 0 0")
os.system("onevdc adddatastore " + usuario + " 0 1")
os.system("onevdc adddatastore " + usuario + " 0 2")

print(f"Creando el usuario {usuario}...")
os.system("oneuser create " + usuario + " " + contrasenya)
os.system("oneuser chgrp " + usuario + " " + usuario)
os.system("oneuser addgroup " + usuario + " " + grupo)

f = open("temp.txt", "w")
f.write(f'''
VM=[
    RUNNING_MEMORY="{ram * 1024}",
    RUNNING_CPU="{cpus}",
    SYSTEM_DISK_SIZE="{disco * 1024}"
]
\n''')
f.write(f'''
DATASTORE=[
    ID="1",
    SIZE="{disco * 1024}"
]
\n''')
f.close()
os.system("oneuser quota " + usuario + " temp.txt")
os.remove("temp.txt")

try:
    print(f"Creando la red {usuario}...")
    f = open("temp.txt", "w")
    f.write(f"NAME = \"{usuario}\"" + "\n")
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
    if publicas > 0:
        f.write("AR=[TYPE = \"IP4\", IP = \""
                + subred[:-1] + str(inicial_publicas) + "\", SIZE = \""
                + str(publicas) + "\" ]" + "\n")
        if privadas > 0:
            f.write("AR=[TYPE = \"IP4\", IP = \""
                    + subred[:-1] + str(inicial_privadas) + "\", SIZE = \""
                    + str(privadas) + "\" ]" + "\n")
    elif privadas > 0:
        f.write("AR=[TYPE = \"IP4\", IP = \""
                + subred[:-1] + str(inicial_privadas) + "\", SIZE = \""
                + str(privadas) + "\" ]" + "\n")
    f.close()
    vnet_id = subprocess.run(['onevnet', 'create', 'temp.txt'],
                             capture_output=True, text=True).stdout.split()[-1]
    print(f"ID: {vnet_id}")
    os.remove("temp.txt")

    os.system("onevdc addvnet " + usuario + " 0 " + vnet_id)
except:
    print("Error al crear la red.")
