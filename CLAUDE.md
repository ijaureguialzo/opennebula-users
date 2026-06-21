# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based toolset for managing OpenNebula cloud infrastructure — creating/deleting users, groups, networks, quotas, and VMs. Scripts run inside a Docker container (`opennebula-cli`) that has the OpenNebula CLI tools installed. All scripts are interactive: they use `click.prompt()` to collect user input, then execute `one*` CLI commands via `os.system()` or `subprocess.run()`.

## Key Directories and Files

- **`scripts/`** — All application logic (9 Python scripts):
  - `crear-usuarios.py` / `borrar-usuarios.py` — Batch create/delete users with groups, quotas, networks, datacenters
  - `crear-usuario.py` / `borrar-usuario.py` — Single user create/delete (full resource setup)
  - `crear-admin.py` — Create admin-level user (assigned to `oneadmin` group)
  - `crear-red.py` — Create a standalone network (no user/group association)
  - `modificar-cuotas.py` — Update quotas for a range of existing users
  - `borrar-maquinas.py` / `borrar-maquinas-usuario.py` — Delete VMs/templates/images for batch/single user
- **`pyproject.toml`** + **`poetry.lock`** — Poetry project (`opennebula-users`, v0.1.0, Python >=3.14)
- **`.env`** — Runtime config: OpenNebula endpoint, RPC URL, credentials (ignored in git)
- **`.token`** — OpenNebula auth token `username:hash` (ignored in git)
- **`Dockerfile`** / **`docker-compose.yml`** — Container image with OpenNebula CLI tools + Python
- **`Makefile`** — All operations go through `make <target>` (see below)

## Common Commands

All commands require `.env` to exist (Makefile fails if missing). Build the Docker image first:

```
make build          # Build the Docker image (docker compose build)
```

### User management (batch)
```
make crear-usuarios     # Batch-create users with groups, quotas, networks, datacenters
make borrar-usuarios    # Batch-delete users and all associated resources (VMs, templates, images)
```

### User management (single)
```
make crear-usuario      # Create a single user with full resource setup (VDC, group, quotas, network)
make borrar-usuario     # Delete a single user and all associated resources
```

### Admin and network
```
make crear-admin        # Create an admin user (oneuser + chgrp to oneadmin)
make crear-red          # Create a standalone network (no user/group association)
```

### Quotas and VMs
```
make modificar-cuotas       # Update quotas for a range of existing users
make borrar-maquinas        # Delete VMs/templates/images for a batch of users
make borrar-maquinas-usuario  # Delete VMs/templates/images for a single user
```

### Maintenance
```
make workspace    # Open interactive shell in the Docker container (/bin/bash)
make clean        # Tear down containers and volumes (docker compose down -v)
```

## Architecture Notes

- **No tests exist.** Scripts are designed for interactive CLI use with live OpenNebula instances.
- **Error handling is minimal** — many scripts use bare `except: pass` (e.g., network creation in `crear-usuarios.py`).
- **Script patterns:** Simple commands use `os.system()` (fire-and-forget); commands that need output (e.g., resource IDs) use `subprocess.run()` with `capture_output=True` and parse stdout.
- **Python 3.14+** is required (per `pyproject.toml`). The only runtime dependency is `click` for interactive prompts.
- **`.env` and `.token` are gitignored** — copy from `env-example` and `token-example` templates before use.

## Convenciones de commits

> **Regla fundamental**: cada funcionalidad completada o corrección de bug debe tener su propio commit independiente. No
> agrupar cambios no relacionados en un mismo commit.

### Cuándo hacer commit

- Al completar una funcionalidad nueva (aunque sea parcial pero funcional).
- Al corregir un bug concreto.
- Al añadir o actualizar documentación relevante.
- **No** hacer commit de código roto o que no compila.

### Formato del mensaje de commit

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<scope>): <descripción breve en imperativo>
```

- **El mensaje debe escribirse en español.**
- Ejemplos de tipos: `feat`, `fix`, `docs`, `refactor`, `chore`.

### Trailer obligatorio

Todo commit creado por un agente de IA debe incluir el trailer con su información de co-autoría al final del mensaje.
