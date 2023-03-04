#!make

help: _header
	${info }
	@echo Opciones:
	@echo ---------------------------------------------
	@echo build
	@echo workspace
	@echo clean
	@echo ---------------------------------------------

_header:
	@echo -----------------------
	@echo OpenNebula User Manager
	@echo -----------------------

build:
	@docker compose build

workspace:
	@docker compose run --rm opennebula-cli /bin/bash

clean:
	@docker compose down -v --remove-orphans
