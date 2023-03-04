#!make

ifneq (,$(wildcard ./.env))
    include .env
    export
else
$(error No se encuentra el fichero .env)
endif

help: _header
	${info }
	@echo Opciones:
	@echo ---------------------------------------------
	@echo build
	@echo crear-usuarios / borrar-usuarios
	@echo workspace
	@echo clean
	@echo ---------------------------------------------

_header:
	@echo -----------------------
	@echo OpenNebula User Manager
	@echo -----------------------

build:
	@docker compose build

crear-usuarios:
	@docker compose run --rm opennebula-cli python3 /scripts/crear_usuarios.py

borrar-usuarios:
	@docker compose run --rm opennebula-cli python3 /scripts/borrar_usuarios.py

workspace:
	@docker compose run --rm opennebula-cli /bin/bash

clean:
	@docker compose down -v --remove-orphans
