# Simulación 3D del sensor inercial BWT901CL

Este proyecto reproduce en una escena 3D las orientaciones (roll, pitch y yaw)
guardadas en `inercial.bin`. La escena se muestra en el navegador y no requiere
conectar el sensor.

## Requisitos

- Python 3.10 o posterior (probado con Python 3.13).
- `pip`.
- Un navegador web.

El programa usa VPython para la escena 3D. También se instala setuptools para
mantener disponible `pkg_resources`, que VPython necesita al iniciarse. Las
demás importaciones del programa (`ctypes`, `math` y `os`) pertenecen a la
biblioteca estándar de Python.

## Instalación en Windows

Abre PowerShell en la carpeta del proyecto y crea un entorno virtual:

```powershell
py -3 -m venv .venv
```

Instala las dependencias dentro del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto, ejecuta:

```powershell
.\.venv\Scripts\python.exe ".\Nuevo proyecto.py"
```

El programa lee `inercial.bin`, que debe permanecer en la misma carpeta que el
script. Al ejecutarlo, imprime la cantidad de paquetes válidos y abre la escena
3D en el navegador. La animación se repite al terminar el archivo; para cerrarla,
interrumpe el programa con `Ctrl+C` en la terminal.

## Datos de entrada

`inercial.bin` contiene tramas binarias de 11 bytes. El programa valida la
cabecera, el tipo de trama de ángulos y el checksum antes de reproducir cada
orientación.
