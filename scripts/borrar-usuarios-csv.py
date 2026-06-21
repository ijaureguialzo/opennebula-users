#!/usr/bin/env python3

import csv
import os
import subprocess

CSV_PATH = "/data/borrar-usuarios.csv"

print()
print("-------------------------------------")
print("--- Borrar usuarios de OpenNebula ---")
print("-------------------------------------")
print()

try:
    with open(CSV_PATH, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_num, row in enumerate(reader, start=2):
            try:
                nombre = row["Nombre"].strip()
                separador = row["Separador"].strip()
                inicial = int(row["Inicial"].strip())
                final = int(row["Final"].strip())
                grupo = row.get("Grupo", "").strip()
                if not grupo:
                    grupo = nombre

            except (KeyError, ValueError) as e:
                print(f"ERROR: Fila {row_num} con datos inválidos ({e}). Se salta esta fila.")
                continue

            print(f"Procesando lote de borrado: {nombre} (IDs {inicial}-{final}), grupo={grupo}")
            print()

            for i in range(inicial, final + 1):
                usuario = nombre + separador + "{0:0>2}".format(i)

                print(f"\nBorrando el usuario {usuario} y sus recursos asociados...\n")

                vm_ids = subprocess.run(
                    ["onevm", "list", usuario, "-l", "id", "--no-header"],
                    capture_output=True, text=True,
                ).stdout.split()
                if len(vm_ids) > 0:
                    print("Borrando las máquinas virtuales...")
                    os.system("onevm recover --delete " + ','.join(vm_ids))

                template_ids = subprocess.run(
                    ["onetemplate", "list", usuario, "-l", "id", "--no-header"],
                    capture_output=True, text=True,
                ).stdout.split()
                if len(template_ids) > 0:
                    print("Borrando las plantillas...")
                    os.system("onetemplate delete --recursive " + ','.join(template_ids))

                image_ids = subprocess.run(
                    ["oneimage", "list", usuario, "-l", "id", "--no-header"],
                    capture_output=True, text=True,
                ).stdout.split()
                if len(image_ids) > 0:
                    print("Borrando las imágenes...")
                    os.system("oneimage delete " + ','.join(image_ids))

                print("Borrando el datacenter...")
                os.system("onevdc delete " + usuario)

                print("Borrando el usuario...")
                os.system("oneuser delete " + usuario)

                print("Borrando el grupo...")
                os.system("onegroup delete " + usuario)

                print("Borrando la red...")
                os.system("onevnet delete " + usuario)

            print(f"\nBorrando el grupo {grupo}...")
            os.system("onegroup delete " + grupo)

        print("\nTodos los lotes procesados.")

except FileNotFoundError:
    print(f"ERROR: No se encontró el fichero {CSV_PATH}.")
    print("Asegúrate de que 'borrar-usuarios.csv' existe en el directorio 'data' montado en /data.")
except Exception as e:
    print(f"ERROR inesperado al leer {CSV_PATH}: {e}")
