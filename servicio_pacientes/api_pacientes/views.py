from django.shortcuts import render
from django.db import connection, DatabaseError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Paciente
from .serializers import PacienteSerializer
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
import sqlite3


logger = logging.getLogger(__name__)

# Página principal
def index(request):
    return render(request, 'api_pacientes/index.html')

# Form registro (envía al endpoint seguro /seguro/registro/ por fetch)
@ensure_csrf_cookie
def registro_page(request):
    return render(request, 'api_pacientes/registro.html')

# Ver perfil (carga info desde DB y muestra)
def perfil_page(request, pk):
    try:
        paciente = Paciente.objects.get(pk=pk)
    except Paciente.DoesNotExist:
        paciente = None
    return render(request, 'api_pacientes/perfil.html', {'paciente': paciente})

# Registro inseguro
@api_view(['POST'])
def registro_inseguro(request):
    nombre = request.data.get('nombre', '')
    fecha_nacimiento = request.data.get('fecha', '')
    email = request.data.get('email', '')
    password = request.data.get('password', '')
    nss = request.data.get('nss', '')

    sql = f"""
        INSERT INTO api_pacientes_paciente (nombre, fecha_nacimiento, nss, email, password, es_doctor)
        VALUES ('{nombre}', '{fecha_nacimiento}', '{nss}', '{email}', '{password}', 0);
        """
    # registrar la consulta para debug
    logger.warning("EJECUTANDO SQL VULNERABLE: %s", sql)

    try:
        with connection.cursor() as cursor:
            # Crear tabla si no existe
            # cursor.execute("""
            #     CREATE TABLE IF NOT EXISTS usuarios (
            #         id INTEGER PRIMARY KEY AUTOINCREMENT,
            #         nombre TEXT NOT NULL,
            #         fecha TEXT NOT NULL,
            #         email TEXT UNIQUE NOT NULL,
            #         password TEXT NOT NULL,
            #         nss TEXT NOT NULL,
            #         es_doctor INTEGER DEFAULT 0
            #     )
            # """)
            # cursor.execute("PRAGMA table_info(api_pacientes_paciente)")
            # columnas = cursor.fetchall()
            # for col in columnas:
            #     print(col)
            cursor.execute(sql)
            # intentar obtener lastrowid (sqlite/otros adaptan)
            try:
                inserted_id = cursor.lastrowid
            except Exception:
                inserted_id = None
        return Response({"status": "ok", "note": "registro_inseguro ejecutado", "id": inserted_id}, status=201)
    except DatabaseError as e:
        # devolver error legible en JSON en vez de traceback 500
        logger.error("SQL Error en registro_inseguro: %s", e, exc_info=True)
        return Response({"status": "error", "detail": str(e)}, status=400)


# --- Registro SEGURO (usa serializer / evita es_doctor) ---
@api_view(['POST'])
def registro_seguro(request):
    serializer = PacienteSerializer(data=request.data)
    if serializer.is_valid():
        paciente = serializer.save()
        data = PacienteSerializer(paciente).data
        return Response(data, status=201)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Obtener perfil (seguro) ---
@api_view(['GET'])
def perfil(request, pk):
    """
    Validando y usando ORM (seguro).
    """
    raw_id = request.GET.get('id', '').strip()
    try:
        pid = int(raw_id)
    except (ValueError, TypeError):
        return Response({"error": "id inválido"}, status=400)

    try:
        paciente = Paciente.objects.get(pk=pid)
    except Paciente.DoesNotExist:
        return Response({}, status=200)

    serializer = PacienteSerializer(paciente)
    return Response(serializer.data, status=200)

#-- Obtener perfil (inseguro)
@api_view(['GET'])
def perfil_inseguro(request):
    """
    Endpoint deliberadamente vulnerable (solo para demo).
    Usa query param ?id=...
    Ejemplo: /api/pacientes/inseguro/perfil/?id=1  or /...?id=1%20OR%201=1
    """
    raw_id = request.GET.get('id', '').strip()
    if raw_id == '':
        return Response({"error": "falta parametro id"}, status=status.HTTP_400_BAD_REQUEST)

    # VULNERABLE: concatenación directa (demostración)
    query = f"SELECT id, nombre, nss, email, es_doctor FROM api_pacientes_paciente WHERE id = {raw_id};"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(cols, r)) for r in rows]
        return Response(results, status=200)
    except DatabaseError as e:
        return Response({"error": "SQL mal formada", "detail": str(e)}, status=400)
