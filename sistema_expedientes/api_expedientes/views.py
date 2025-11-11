from django.shortcuts import render

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import NotaMedica
from .serializers import NotaMedicaSerializer

# --- Página de inicio ---
def index(request):
    return render(request, "api_expedientes/index.html")


# --- Página formulario para crear nota médica ---
def crear_nota_page(request):
    return render(request, "api_expedientes/crear_nota.html")


# --- Página para buscar notas de un paciente ---
def buscar_notas_page(request):
    return render(request, "api_expedientes/buscar_notas.html")



# --- INSEGURO: SQL Injection por concatenación ---
@api_view(['GET'])
def buscar_inseguro(request):
    nss = request.GET.get("nss", "")
    if nss == '':
        return Response({"error": "falta parametro nss"}, status=status.HTTP_400_BAD_REQUEST)

    query = f"SELECT * FROM api_expedientes_notamedica WHERE CAST(nss_paciente AS TEXT) = '{nss}';"
    # Simulamos lookup por nss, pero dejando vulnerabilidad
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return Response(results)


# --- SEGURO: ORM, sin SQL Injection ---
@api_view(['GET'])
def buscar_seguro(request):
    nss = request.GET.get("nss", "")
    try:
        pid = int(nss)
    except (ValueError, TypeError):
        return Response([], status=200)
    
    notas = NotaMedica.objects.filter(nss_paciente=pid)
    serializer = NotaMedicaSerializer(notas, many=True)
    return Response(serializer.data)


# --- Crear nota médica (Seguro) ---
@api_view(['POST'])
def crear_nota(request):
    serializer = NotaMedicaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
