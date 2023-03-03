#!/usr/bin/env python3

import os

inicial = int(input("Usuario inicial (ej. 1): "))
final = int(input("Usuario final (ej. 15): "))

for i in range(inicial, final + 1):
    usuario = "ciber_" + "{0:0>2}".format(i)

    os.system("onevdc delete " + usuario)
    os.system("oneuser delete " + usuario)
    os.system("onegroup delete " + usuario)
    os.system("onevnet delete " + usuario)
