# CLAUDE.md — ALGARROBO_BASE2

## ¿Qué es este proyecto?
Este repositorio forma parte de la Unidad de Información y Análisis (UIA) de CONAF.

---

## Comandos de Referencia Rápida
- **Ejecutar servidor local:** `cd backend && python main.py`
- **Instalar dependencias:** `cd backend && pip install -r requirements.txt`
- **Ejecutar pruebas:** `cd backend && pytest`

## Tecnología y Stack
- **Backend:** Python (Flask)
- **Librerías principales:** flask, flask-cors, psycopg2-binary, bcrypt, python-dotenv, PyPDF2, python-docx, openpyxl, Pillow, pytesseract

## Guía de Estilo y Convenciones
- **Idioma del código:** Inglés para infraestructura, nombres de variables y funciones. Español para comentarios de negocio e interfaz de usuario.
- **Backend Python:** Cumplir con PEP 8. Estilo `snake_case` para variables, funciones y nombres de archivos; `PascalCase` para clases.
- **Trazabilidad:** Cada cambio debe rastrearse directamente a un requerimiento o corrección solicitada.


## Directrices de Desarrollo (Claude Code)

### 1. Pensar antes de Codificar
- **No asumas:** Si hay ambigüedad o múltiples interpretaciones, pregunta antes de codificar.
- **Simplifica:** Elige el camino más simple y limpio. Evita la sobreingeniería y abstracciones innecesarias.

### 2. Cambios Quirúrgicos
- Modifica únicamente las líneas necesarias para cumplir el objetivo.
- No realices refactorizaciones no solicitadas en código adyacente.
- Respeta estrictamente el formato y estilo del archivo existente.

### 3. Ejecución Orientada a Objetivos
- Define el criterio de éxito para cada cambio.
- Comprueba que tus modificaciones no introduzcan errores de compilación o de linting.
