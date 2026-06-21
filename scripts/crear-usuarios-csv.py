#!/usr/bin/env python3

import csv
import os
import subprocess

CSV_DEFAULT = "usuarios.csv"


def _run(cmd):
    """Ejecuta un comando con os.system y avisa si falla."""
    ret = os.system(cmd)
    if ret != 0:
        print(f"  [ADVERTENCIA] comando falló (código {ret}): {cmd}")


print()
print("------------------------------------")
print("--- Crear usuarios de OpenNebula ---")
print("------------------------------------")
print()

csv_file = input(f"Nombre del fichero CSV (por defecto [{CSV_DEFAULT}]): ").strip()
if not csv_file:
    csv_file = CSV_DEFAULT

CSV_PATH = "/data/" + csv_file

try:
    with open(CSV_PATH, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_num, row in enumerate(reader, start=2):
            try:
                nombre = row["Nombre"].strip()
                separador = row["Separador"].strip()
                inicial = int(row["Inicial"].strip())
                final = int(row["Final"].strip())
                contrasenya = row["Contraseña"].strip()
                grupo = row["Grupo"].strip()

                cpus = float(row["CPUs"].strip())
                ram = float(row["RAM (GiB)"].strip())
                disco = float(row["Disco (GiB)"].strip())

                subred = row["Subred"].strip()
                mascara = row["Máscara"].strip()
                gateway = row["Gateway"].strip()
                dns = row["DNS"].strip()
                publicas = int(row["Públicas"].strip())
                inicial_publicas = int(row["Inicio públicas"].strip())
                privadas = int(row["Privadas"].strip())
                inicial_privadas = int(row["Inicio privadas"].strip())

            except (KeyError, ValueError) as e:
                print(f"ERROR: Fila {row_num} con datos inválidos ({e}). Se salta esta fila.")
                continue

            print(f"Procesando lote: {nombre} (IDs {inicial}-{final}) ...")
            print(f"--- Datos del lote: grupo={grupo}, cpus={cpus}, ram={ram}GiB, disco={disco}GiB ---")
            print(f"--- Red: subred={subred}, mascara={mascara}, gateway={gateway}, dns={dns} ---")
            print(f"--- IPs públicas: {publicas} (inicio={inicial_publicas}), privadas: {privadas} (inicio={inicial_privadas}) ---")
            print()

            # Crear recursos compartidos del lote (grupo padre, VDC)
            print(f"Creando el grupo {grupo}...")
            _run("onegroup create " + grupo)
            _run("onevdc delgroup default " + grupo)

            for i in range(inicial, final + 1):
                usuario = nombre + separador + "{0:0>2}".format(i)

                try:
                    print(f"\nCreando el usuario {usuario} y sus recursos asociados...\n")

                    # Datacenter
                    print(f"Creando el datacenter {usuario}...")
                    _run("onevdc create " + usuario)

                    # Grupo con ACLs
                    print(f"Creando el grupo {usuario}...")
                    group_id = subprocess.run(
                        ["onegroup", "create", usuario, "--resources",
                         "VM+IMAGE+TEMPLATE+DOCUMENT+VROUTER+VMGROUP+NET"],
                        capture_output=True, text=True,
                    ).stdout.split()[-1]
                    print(f"ID: {group_id}")
                    _run(f'oneacl create "@{group_id} CLUSTER/* ADMIN"')
                    _run(f'oneacl create "@{group_id} NET/* ADMIN"')

                    # Sunstone config
                    f = open("temp.txt", "w")
                    f.write("SUNSTONE=[")
                    f.write(
                        'DEFAULT_VIEW="user", GROUP_ADMIN_DEFAULT_VIEW="groupadmin", '
                    )
                    f.write('GROUP_ADMIN_VIEWS="groupadmin", VIEWS="cloud,user"')
                    f.write("]")
                    f.close()
                    _run("onegroup update " + usuario + " temp.txt")
                    os.remove("temp.txt")

                    # VDC associations
                    _run("onevdc addgroup " + usuario + " " + usuario)
                    _run("onevdc delgroup default " + usuario)
                    _run("onevdc addhost " + usuario + " 0 localhost")
                    _run("onevdc adddatastore " + usuario + " 0 0")
                    _run("onevdc adddatastore " + usuario + " 0 1")
                    _run("onevdc adddatastore " + usuario + " 0 2")

                    # Usuario con credenciales
                    print(f"Creando el usuario {usuario}...")
                    _run("oneuser create " + usuario + " " + contrasenya)
                    _run("oneuser chgrp " + usuario + " " + usuario)
                    _run("oneuser addgroup " + usuario + " " + grupo)

                    # Quotas
                    f = open("temp.txt", "w")
                    f.write(f"""
    VM=[
        RUNNING_MEMORY="{ram * 1024}",
        RUNNING_CPU="{cpus}",
        SYSTEM_DISK_SIZE="{disco * 1024}"
    ]
    \n""")
                    f.write(f"""
    DATASTORE=[
        ID="1",
        SIZE="{disco * 1024}"
    ]
    \n""")
                    f.close()
                    _run("oneuser quota " + usuario + " temp.txt")
                    os.remove("temp.txt")

                    # Red (ya tenía try/except, se mantiene)
                    try:
                        print(f"Creando la red {usuario}...")
                        f = open("temp.txt", "w")
                        f.write(f"NAME = \"{usuario}\"" + "\n")
                        f.write("BRIDGE = \"aulas\"" + "\n")
                        f.write("BRIDGE_TYPE = \"linux\"" + "\n")
                        f.write(f"DNS = \"{dns}\"" + "\n")
                        f.write(f"GATEWAY = \"{gateway}\"" + "\n")
                        f.write("NETWORK_MASK = \"" + mascara + "\"" + "\n")
                        f.write("OUTER_VLAN_ID = \"\"" + "\n")
                        f.write("PHYDEV = \"\"" + "\n")
                        f.write("SECURITY_GROUPS = \"0\"" + "\n")
                        f.write("VLAN_ID = \"\"" + "\n")
                        f.write("VN_MAD = \"fw\"" + "\n")
                        if publicas > 0:
                            f.write("AR=[TYPE = \"IP4\", IP = \""
                                    + subred[:-1]
                                    + str(publicas * (i - 1) + inicial_publicas)
                                    + "\", SIZE = \"" + str(publicas) + "\" ]" + "\n")
                            if privadas > 0:
                                f.write("AR=[TYPE = \"IP4\", IP = \""
                                        + subred[:-1]
                                        + str(privadas * (i - 1) + inicial_privadas)
                                        + "\", SIZE = \"" + str(privadas) + "\" ]" + "\n")
                        elif privadas > 0:
                            f.write("AR=[TYPE = \"IP4\", IP = \""
                                    + subred[:-1]
                                    + str(privadas * (i - 1) + inicial_privadas)
                                    + "\", SIZE = \"" + str(privadas) + "\" ]" + "\n")
                        f.close()
                        vnet_id = subprocess.run(
                            ["onevnet", "create", "temp.txt"],
                            capture_output=True, text=True,
                        ).stdout.split()[-1]
                        print(f"ID: {vnet_id}")
                        os.remove("temp.txt")

                        _run("onevdc addvnet " + usuario + " 0 " + vnet_id)
                    except Exception:
                        print("Error al crear la red.")

                except Exception as e:
                    print(f"ERROR al procesar {usuario}: {e}. Se salta este usuario.")
                    continue

                print()

            print(f"\n--- Lote {nombre} completado ---\n")

    print("Todos los lotes procesados.")

except FileNotFoundError:
    print(f"ERROR 0: No se encontró el fichero {CSV_PATH}.")
    print("Asegúrate de que el directorio 'data' está montado en /data dentro del contenedor.")
    exit(1)
except Exception as e:
    print(f"ERROR inesperado al leer {CSV_PATH}: {e}")
