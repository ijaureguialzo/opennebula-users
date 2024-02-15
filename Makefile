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
	@echo --------------------------------
	@echo build
	@echo --------------------------------
	@echo crear-usuarios / borrar-usuarios
	@echo modificar-cuotas
	@echo --------------------------------
	@echo crear-usuario / crear-admin
	@echo --------------------------------
	@echo workspace
	@echo clean
	@echo --------------------------------

_header:
	@echo -----------------------
	@echo OpenNebula User Manager
	@echo -----------------------

build:
	@docker compose build

crear-usuarios:
	@docker compose run --rm opennebula-cli python3 /scripts/crear-usuarios.py

borrar-usuarios:
	@docker compose run --rm opennebula-cli python3 /scripts/borrar-usuarios.py

crear-usuario:
	@docker compose run --rm opennebula-cli python3 /scripts/crear-usuario.py

crear-admin:
	@docker compose run --rm opennebula-cli python3 /scripts/crear-admin.py

modificar-cuotas:
	@docker compose run --rm opennebula-cli python3 /scripts/modificar-cuotas.py

workspace:
	@docker compose run --rm opennebula-cli /bin/bash

clean:
	@docker compose down -v --remove-orphans
