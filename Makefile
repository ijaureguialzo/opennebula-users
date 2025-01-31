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
	@echo borrar-maquinas
	@echo --------------------------------
	@echo crear-usuario / crear-admin
	@echo crear-red
	@echo borrar-usuario
	@echo borrar-maquinas-usuario
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

crear-red:
	@docker compose run --rm opennebula-cli python3 /scripts/crear-red.py

crear-admin:
	@docker compose run --rm opennebula-cli python3 /scripts/crear-admin.py

borrar-usuario:
	@docker compose run --rm opennebula-cli python3 /scripts/borrar-usuario.py

modificar-cuotas:
	@docker compose run --rm opennebula-cli python3 /scripts/modificar-cuotas.py

borrar-maquinas:
	@docker compose run --rm opennebula-cli python3 /scripts/borrar-maquinas.py

borrar-maquinas-usuario:
	@docker compose run --rm opennebula-cli python3 /scripts/borrar-maquinas-usuario.py

workspace:
	@docker compose run --rm opennebula-cli /bin/bash

clean:
	@docker compose down -v --remove-orphans
