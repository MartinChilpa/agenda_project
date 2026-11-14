# agenda_project

Proyecto Django para gestionar agenda, citas y proveedores.

## Tecnologías

- Python
- Django
- Django REST Framework
- SQLite (por defecto para desarrollo)

## Requisitos

- Python 3.10+
- pip
- virtualenv (opcional pero recomendado)

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Variables de entorno

Crea un archivo `.env` si tu proyecto lo requiere y define las variables necesarias antes de ejecutar la aplicación.

## Uso

- Inicia el servidor con:

```bash
python manage.py runserver
```

- Accede en tu navegador a:

```text
http://127.0.0.1:8000/
```

## Estructura principal

- `agenda/`: lógica de la app de agenda y citas.
- `accounts/`: autenticación y gestión de usuarios.
- `config/`: configuración principal del proyecto Django.
- `manage.py`: punto de entrada para ejecutar comandos de Django.

## Licencia

Este proyecto no incluye una licencia específica por el momento.
