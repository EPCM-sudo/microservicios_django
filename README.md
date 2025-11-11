# microservicios_django
sistema de expedientes médicos que demuestra, de manera práctica, las vulnerabilidades críticas de seguridad (como SQL Injection y Asignación Masiva) al usar consultas SQL directas y la mitigación de las mismas mediante el uso correcto de un ORM y serializadores de datos.

# 🧠 Proyecto: Sistema de Microservicios Django — Pacientes y Expedientes

Este proyecto implementa una arquitectura de **microservicios con Django REST Framework**, demostrando el uso de servicios **seguros e inseguros** para el manejo de pacientes y expedientes médicos.  
Incluye ejemplos deliberadamente vulnerables para estudiar **inyección SQL** y **asignación masiva**, así como sus contrapartes seguras.

---

## 📁 Estructura del Proyecto

microservicios_django/
│
├── servicio_pacientes/ # Microservicio 1
│ ├── api_pacientes/ # App principal (endpoints seguros/inseguros)
│ ├── manage.py
│ 
│
├── sistema_expedientes/ # Microservicio 2
│ ├── api_expedientes/ # App principal (endpoints seguros/inseguros)
│ ├── manage.py
│
│
└── README.md # Este archivo
└── requirements.txt


---

## ⚙️ Requisitos previos

- Python **3.11+**
- pip
- Git
- (opcional) Postman o Thunder Client para pruebas API

---

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/EPCM-sudo/microservicios_django.git
cd microservicios_django

```
### Creat entorno virtual
```bash
python -m venv venv
# Activar (Windows)
venv\Scripts\activate
# Activar (Linux/Mac)
source venv/bin/activate
```

## 🩺 Microservicio 1: Servicio de Pacientes

### 📦 Instalación de dependencias
```bash
cd servicio_pacientes
pip install -r requirements.txt
```
### 🧱 Migraciones iniciales
```bash
python manage.py makemigrations
python manage.py migrate
```
### 🧍‍♂️ Crear usuario administrador (opcional)
```bash
python manage.py createsuperuser
```
### ▶️ Ejecutar el servidor
```bash
python manage.py runserver 8000
```
### 🌐 Endpoints principales

Tipo	 Endpoint	                                        Descripción
POST	/api/pacientes/inseguro/registro/	                Registro vulnerable (SQL Injection / mass assignment)
POST	/api/pacientes/seguro/registro/	                    Registro protegido (ORM, validaciones)
GET 	/api/pacientes/seguro/perfil/<id>/	                Consulta de perfil segura
PUT	    /api/pacientes/inseguro/perfil/<id>/	            Actualización insegura (demostración)
PUT	    /api/pacientes/seguro/perfil/actualizar/<id>/	    Actualización segura

## 📘 Microservicio 2: Sistema de Expedientes
### 📦 Instalación de dependencias
```bash
cd ../sistema_expedientes
pip install -r requirements.txt
```
### 🧱 Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```
### ▶️ Ejecutar servidor
```bash
python manage.py runserver 8001
```
### 🌐 Endpoints principales
Tipo	Endpoint	                                Descripción
GET	    /api/expedientes/inseguro/buscar?nss=...	Búsqueda vulnerable (inyección SQL)
GET	    /api/expedientes/seguro/buscar?nss=...	    Búsqueda protegida (consultas parametrizadas)

## 🧠 Pruebas sugeridas

Usa Postman o Thunder Client para probar ambos microservicios:

Crear pacientes (seguro e inseguro).

Intentar modificar es_doctor desde ambos endpoints y observar resultados.

Buscar expedientes con nss=9999' OR 1=1 -- para demostrar la diferencia entre consultas seguras e inseguras.

Registrar evidencias (capturas de pantalla y respuestas JSON).

## 🧰 Herramientas utilizadas

Python 3.13

Django 5.x

Django REST Framework

SQLite 3

Postman
 o Thunder Client

GitHub para control de versiones

## 🔐 Seguridad y objetivos didácticos

Este proyecto está diseñado para demostrar buenas y malas prácticas en el desarrollo de APIs:

Tema	                Endpoint inseguro	                    Endpoint seguro
SQL Injection	        buscar_inseguro, registro_inseguro	    buscar_seguro, registro_seguro
Mass Assignment	        actualizar_inseguro	                    actualizar_seguro
Validación de entrada	❌	                                    ✅
ORM vs SQL directo	    ❌ SQL manual	                        ✅ Django ORM

⚠️ Nota: los endpoints inseguros no deben usarse en producción, su propósito es educativo.

## 🧩 Autores / Créditos

Autor: Eugenio Pacelli Chávez Macedo
Materia: Seguridad en el Desarrollo de Aplicaciones
Docente: Abel ALberto Pintor Estrada
Institución: Instituto Tecnologico de Morelia
Año: 2025