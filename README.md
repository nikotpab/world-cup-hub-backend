# World Cup Hub - Backend Service

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=flat&logo=mysql&logoColor=white)

## 1. Descripción del Proyecto
[cite_start]**World Cup Hub** es una plataforma orientada a la experiencia digital del Mundial de la FIFA 2026[cite: 7]. [cite_start]Este servicio de backend gestiona la complejidad logística de un evento multinacional, proporcionando un núcleo informativo y operacional para aficionados y equipos de operaciones[cite: 5, 10].

[cite_start]El sistema se centra en la **transparencia y trazabilidad**, registrando cada evento relevante (cambios de calendario, notificaciones, transferencias) de forma auditable[cite: 14].

## 2. Características Principales (MVP)
* [cite_start]**Gestión de Usuarios y Preferencias**: Registro, inicio de sesión y configuración de agendas personales basadas en selecciones y sedes favoritas[cite: 29, 47].
* [cite_start]**Seguimiento de Partidos**: Ingesta de datos de proveedores externos sobre equipos, partidos y resultados en tiempo real[cite: 51].
* [cite_start]**Módulo de "Pollas" Futboleras**: Juego social de predicciones por puntos con cálculo automático de puntajes y rankings[cite: 31, 32].
* [cite_start]**Álbum Digital**: Sistema de colección de láminas, apertura de paquetes e intercambio entre usuarios de la comunidad[cite: 36, 76].
* [cite_start]**Ticketing y Pagos**: Gestión del ciclo de vida de entradas (Disponible -> Reservada -> Pagada) con transiciones trazables[cite: 82].
* [cite_start]**Auditoría y Soporte**: Registro de transacciones para investigación de casos y cumplimiento[cite: 67, 68].

## 3. Stack Tecnológico
* **Lenguaje**: Python 3.13.
* **Framework Web**: Flask.
* **Persistencia**: SQLAlchemy ORM con soporte para MySQL.
* **Serialización**: Marshmallow-SQLAlchemy para la gestión de modelos y esquemas.
* **Seguridad**: Autenticación mediante JWT (JSON Web Tokens) y hashing de contraseñas con Argon2.
* **Pruebas**: Pytest y unittest.mock para validación de lógica de negocio.

## 4. Estructura del Proyecto
[cite_start]El backend sigue una arquitectura orientada a servicios con separación clara de responsabilidades[cite: 132]:

```text
src/
├── database/          # Configuración de persistencia y base de datos
├── models/            # Definición de entidades de dominio (User, Match, Ticket, etc.)
├── services/          # Lógica de negocio y servicios (AuthenticationService)
├── test/              # Suite de pruebas unitarias y mocks
├── __init__.py        # Fábrica de la aplicación
config.py              # Configuraciones de entorno (Development/Production)
run.py                 # Punto de entrada para la ejecución del servidor
