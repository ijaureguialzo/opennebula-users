#!/usr/bin/env python3

import os

inicial = int(input("Usuario inicial (ej. 1): "))
final = int(input("Usuario final (ej. 15): "))

for i in range(inicial, final + 1):
    usuario = "ciber_" + "{0:0>2}".format(i)

    os.system("onevdc create " + usuario)
    os.system("onegroup create " + usuario)

    f = open("temp.txt", "w")
    f.write(
        "SUNSTONE=[DEFAULT_VIEW=\"user\", GROUP_ADMIN_DEFAULT_VIEW=\"groupadmin\", GROUP_ADMIN_VIEWS=\"groupadmin\", VIEWS=\"cloud,user\"]")
    f.close()
    os.system("onegroup update " + usuario + " temp.txt")
    os.remove("temp.txt")

    os.system("onevdc addgroup " + usuario + " " + usuario)
    os.system("onevdc delgroup default " + usuario)
    os.system("onevdc addhost " + usuario + " 0 localhost")
    os.system("onevdc adddatastore " + usuario + " 0 0")
    os.system("onevdc adddatastore " + usuario + " 0 1")
    os.system("onevdc adddatastore " + usuario + " 0 2")

    os.system("oneuser create " + usuario + " 12345Abcde")
    os.system("oneuser chgrp " + usuario + " " + usuario)
    os.system("oneuser addgroup " + usuario + " ciberseguridad")

    f = open("temp.txt", "w")
    f.write("VM=[MEMORY=\"12288\", CPU=\"4\", SYSTEM_DISK_SIZE=\"65536\"]")
    f.close()
    os.system("oneuser quota " + usuario + " temp.txt")
    os.remove("temp.txt")

    f = open("temp.txt", "w")
    f.write("NAME = \"" + usuario + "\"" + "\n")
    f.write("BRIDGE = \"aulas\"" + "\n")
    f.write("BRIDGE_TYPE = \"linux\"" + "\n")
    f.write("DNS = \"192.168.10.1 1.1.1.1\"" + "\n")
    f.write("GATEWAY = \"172.20.1.2\"" + "\n")
    f.write("NETWORK_MASK = \"255.255.0.0\"" + "\n")
    f.write("OUTER_VLAN_ID = \"\"" + "\n")
    f.write("PHYDEV = \"\"" + "\n")
    f.write("SECURITY_GROUPS = \"0\"" + "\n")
    f.write("VLAN_ID = \"\"" + "\n")
    f.write("VN_MAD = \"fw\"" + "\n")
    f.write("AR=[TYPE = \"IP4\", IP = \"172.20.227." + str(i) + "\", SIZE = \"1\" ]" + "\n")
    f.write("AR=[TYPE = \"IP4\", IP = \"172.20.227." + str(10 * (i - 1) + 50) + "\", SIZE = \"10\" ]" + "\n")
    f.close()
    os.system("onevnet create temp.txt")
    os.remove("temp.txt")

    os.system("onevdc addvnet " + usuario + " 0 " + usuario)
