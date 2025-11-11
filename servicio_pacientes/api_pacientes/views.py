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
from .utils import bool_to_int
import re

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
    es_doctor = bool_to_int(request.data.get('es_doctor', False))

    sql = f"""
        INSERT INTO api_pacientes_paciente (nombre, fecha_nacimiento, nss, email, password, es_doctor)
        VALUES ('{nombre}', '{fecha_nacimiento}', '{nss}', '{email}', '{password}', '{es_doctor}');
        """
    # registrar la consulta para debug
    logger.warning("EJECUTANDO SQL VULNERABLE: %s", sql)

    try:
        with connection.cursor() as cursor: 
            cursor.execute(sql)
            inserted_id = cursor.lastrowid

            # Consultar el usuario recién creado usando f-string (seguro porque inserted_id es int)
            cursor.execute(f"""
                SELECT id, nombre, fecha_nacimiento, nss, email, es_doctor 
                FROM api_pacientes_paciente 
                WHERE id = {inserted_id}
            """)

            usuario = cursor.fetchone()
            
            if usuario:
                return Response({
                    'status': 'success',
                    'message': 'Usuario creado (método inseguro)',
                    'usuario_creado': {
                        'id': usuario[0],
                        'nombre': usuario[1],
                        'fecha_nacimiento': usuario[2],
                        'nss': usuario[3],
                        'email': usuario[4],
                        'es_doctor': bool(usuario[5]),
                    },
                    'warning': '⚠️ VULNERABLE A INYECCIÓN SQL',
                    'sql_ejecutado': sql
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Usuario creado pero no se pudo recuperar',
                    'id': inserted_id
                }, status=status.HTTP_201_CREATED)
                
    except DatabaseError as e:
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
    Versión segura del perfil: usa el ORM y el parámetro <pk> de la URL.
    """
    try:
        paciente = Paciente.objects.get(pk=pk)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=404)

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

#Modificar usuario inseguro
@api_view(['PUT'])
def actualizar_perfil_inseguro(request, id):
    """
    Endpoint inseguro: actualiza datos del paciente concatenando directamente SQL.
    Vulnerable a SQL Injection y mass assignment.
    """
    data = request.data

    # Construcción manual de pares campo=valor
    updates = []
    for key, value in data.items():
        # convertir booleanos o None
        if key == 'es_doctor':
            v = bool_to_int(value)
            updates.append(f"{key} = {v}")
        elif value is None:
            updates.append(f"{key} = NULL")
        else:
            # escape mínimo (no protege de inyección real)
            val = str(value).replace("'", "''")
            updates.append(f"{key} = '{val}'")

    if not updates:
        return Response({"error": "No hay campos para actualizar"}, status=400)

    sql = f"UPDATE api_pacientes_paciente SET {', '.join(updates)} WHERE id = {id};"

    logger.warning("EJECUTANDO SQL INSEGURA: %s", sql)

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return Response({"status": "ok", "note": "Actualización insegura ejecutada", "datos":updates}, status=200)
    except DatabaseError as e:
        logger.error("Error SQL inseguro: %s", e, exc_info=True)
        return Response({"error": "Fallo en consulta insegura", "detail": str(e)}, status=400)

#Modificar usuario seguro
@api_view(['PUT'])
def actualizar_perfil_seguro(request, id):
    """
    Endpoint seguro: usa ORM y validaciones para actualizar el perfil.
    Solo permite modificar campos específicos.
    """
    try:
        paciente = Paciente.objects.get(pk=id)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=404)

    # Campos permitidos (whitelist)
    campos_permitidos = {'nombre', 'fecha_nacimiento', 'email', 'nss', 'password'}

    # Filtrar los datos entrantes
    data = {k: v for k, v in request.data.items() if k in campos_permitidos}

    # Validar formato NSS (ejemplo)
    if 'nss' in data and not re.fullmatch(r'^[0-9]{4,30}$', data['nss']):
        return Response({"error": "NSS inválido"}, status=400)

    serializer = PacienteSerializer(paciente, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        result = serializer.data
        result.pop('password', None)  # no exponer contraseña
        return Response(result, status=200)
    else:
        return Response(serializer.errors, status=400)
