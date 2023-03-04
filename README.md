# opennebula-users

Scripts para crear y borrar usuarios en OpenNebula.

## Prerrequisitos

1. Crear los ficheros `.env` y `.token` a partir de `env-example` y `token-example`.

2. Instalar Docker Desktop para [Windows y macOS](https://www.docker.com/products/docker-desktop/)
   o [Linux](https://docs.docker.com/desktop/linux/install/).

3. En Windows, instalar [Scoop](https://scoop.sh) usando PowerShell:

   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
   Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh')
   ```

   Y después instalar los comandos necesarios:

   ```powershell
   scoop install make
   ```

4. Construir el contenedor::

    ```shell
    make build
    ```

## Funcionamiento

Crear usuarios:

```shell
make crear-usuarios
```

Borrar usuarios:

```shell
make borrar-usuarios
```

## Referencias

- [Command Line Interface](https://docs.opennebula.io/6.6/management_and_operations/references/cli.html)
- [How to Set Up a CLI Client for an OpenNebula Frontend](https://support.opennebula.pro/hc/en-us/articles/360042509712-How-to-Set-Up-a-CLI-Client-for-an-OpenNebula-Frontend)
- [OpenNebula Repositories](https://docs.opennebula.io/6.6/installation_and_configuration/frontend_installation/opennebula_repository_configuration.html#community-edition)
- [OpenNebula CLI Tools](https://github.com/tinova/one-tools)
- [Debian - Official Image](https://hub.docker.com/_/debian)
