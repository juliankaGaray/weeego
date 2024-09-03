import pyodbc
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,authenticate
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime

from django.http import StreamingHttpResponse
import time
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib import messages


import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
import pyodbc
from django.conf import settings


# Create your views here.

@login_required
def index(request): 
    rol = request.session.get('rol', '')
    print(f"Rol del usuario: {rol}")  # Depurar el rol
    return render(request, 'accounts/index.html', {'rol': rol})

@login_required
def productos_template(request):
    rol = request.session.get('rol', '')
    return render(request, 'accounts/productos.html', {'rol': rol})


@login_required    
def vehiculos_template(request):
    rol = request.session.get('rol', '')
    return render(request, 'accounts/vehiculos.html', {'rol': rol})

@login_required
def recolecciones_template(request):
    rol = request.session.get('rol', '')
    return render(request, 'accounts/recolecciones.html', {'rol': rol})

@login_required
def clientes_template(request):
    rol = request.session.get('rol', '')
    return render(request, 'accounts/clientes.html', {'rol': rol})   

@login_required
def cotizacion_template(request):
    rol = request.session.get('rol', '')
    print(rol)
    return render(request,'accounts/cotizaciones.html', {'rol': rol}) 

@login_required
def inventario_template(request):
    rol = request.session.get('rol', '')
    print(rol)
    return render(request,'accounts/inventario.html', {'rol': rol}) 



def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        clave = request.POST.get('clave')
        next_url = request.POST.get('next', 'index')
        
        conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        user_record = cursor.fetchone()
    
        if user_record and check_password(clave, user_record[2]):
            try:
                user, created = User.objects.get_or_create(
                    id=user_record[0],
                    defaults={
                        'email': email,
                        'password': user_record[2],
                        'username': email  
                    }
                )
            except IntegrityError:
             
                user = User.objects.get(email=email)
                user.email = email
                user.set_password(user_record[2])
                user.save()
                created = False

            if not created:
                user.email = email
                user.set_password(user_record[2])
                user.save()
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            request.session['rol'] = user_record[4]
            request.session['usuario'] = user_record[3]
            return redirect(next_url)
        else:
            context = {'error': 'Contraseña o email incorrecto', 'next': next_url}
            print(context)
            return render(request, 'accounts/login.html', context)
    
    next_url = request.GET.get('next', 'index')
    return render(request, 'accounts/login.html', {'next': next_url})


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('clave')
        nombre = request.POST.get('nombre')
        rol = request.POST.get('rol')
        email = request.POST.get('email')
        fecha = request.POST.get('fecha')



        hashed_password = make_password(password)

     
        conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()

       
        cursor.execute('INSERT INTO usuarios (nombre_usuario,contrasena,nombre_completo,rol,email,fecha_creacion) VALUES (?, ?, ?,?,?,?)',(username,hashed_password,nombre,rol,email, fecha))
        conn.commit()
        conn.close()

        return redirect('login')
    
    return render(request, 'accounts/registro.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def productos(request):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("SELECT * from Rutas")
    rows = cursor.fetchall()


    productos = []
    for row in rows:
        productos.append({
          'id': row[0],
                'nombre': row[1],
                'descripcion' : row[2] 
        })

    print(productos)
    cursor.close()
    conn.close()

    return JsonResponse({'productos': productos})


@login_required
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def producto_detalle(request, product_id=None):
    if request.method == "GET" and product_id:
        conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rutas WHERE ruta_id=?", (product_id,))
        row = cursor.fetchone()
        if row:
            producto = {
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2]
            }
            cursor.close()
            conn.close()
            return JsonResponse(producto)
        else:
            cursor.close()
            conn.close()
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)

    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            nombre = data.get('nombre')
            descripcion = data.get('descripcion')
            

            if not all([nombre, descripcion]):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rutas (nombre, descripcion)
                VALUES (?, ?)
            """, (nombre, descripcion))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "PUT" and product_id:
        try:
            data = json.loads(request.body.decode('utf-8'))
            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rutas
                SET nombre=?, descripcion=?
                WHERE ruta_id=?
            """, (data['nombre'], data['descripcion'], product_id))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest()



@login_required
def vehiculos(request):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("SELECT * from Vehículos")
    rows = cursor.fetchall()


    vehiculos = []
    for row in rows:
        vehiculos.append({
          'id': row[0],
                'placa': row[1],
                'modelo' : row[2],
                'capacidad': row[3]
        })

 
    cursor.close()
    conn.close()

    return JsonResponse({'vehiculos': vehiculos})


@login_required
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def vehiculos_detalle(request, vehiculo_id=None):
    if request.method == "GET" and vehiculo_id:
        conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Vehículos WHERE vehiculo_id=?", (vehiculo_id,))
        row = cursor.fetchone()
        if row:
            vehiculos = {
                'id': row[0],
                  'placa': row[1],
                'modelo' : row[2],
                'capacidad': row[3]
            }
            cursor.close()
            conn.close()
            return JsonResponse(vehiculos)
        else:
            cursor.close()
            conn.close()
            return JsonResponse({'error': 'Vehiculo no encontrado'}, status=404)

    elif request.method == "POST":
        print("Entro al if")
        try:
            data = json.loads(request.body.decode('utf-8'))
            placa = data.get('placa')
            modelo = data.get('modelo')
            capacidad = data.get('capacidad')
           

            if not all([placa, modelo, capacidad]):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Vehículos (placa, modelo, capacidad)
                VALUES (?, ?, ?)
            """, (placa, modelo, capacidad))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "PUT" and vehiculo_id:
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Vehículos
                SET placa=?, modelo=?, capacidad=?
                WHERE vehiculo_id=?
            """, (data['placa'], data['modelo'],data['capacidad'], vehiculo_id))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest()


@login_required
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def recolecciones(request):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()

    if request.method == "GET":
        # Fetch all recolecciones
        cursor.execute("""
            SELECT rec.recogida_id, CLI.nombre, emp.nombre, rut.descripcion, vehi.placa, tip.descripcion, rec.fecha, rec.hora, rec.cantidad
            FROM Recogidas rec
            INNER JOIN Clientes CLI ON CLI.cliente_id = rec.cliente_id
            INNER JOIN Empleados emp ON emp.empleado_id = rec.empleado_id
            INNER JOIN Rutas rut ON rec.ruta_id = rut.ruta_id
            INNER JOIN Vehículos vehi ON rec.vehiculo_id = vehi.vehiculo_id
            INNER JOIN Tipos_de_Basura tip ON rec.tipo_basura_id = tip.tipo_basura_id
        """)
        rows = cursor.fetchall()

        recolecciones = []
        for row in rows:
            recolecciones.append({
                'id': row[0],
                'Cliente': row[1],
                'Empleado': row[2],
                'Ruta': row[3],
                'Placa': row[4],
                'Tipo_basura': row[5],
                'Fecha': row[6],
                'Hora': row[7],
                'Cantidad': row[8],
            })

        # Fetch selection data
        cursor.execute("SELECT cliente_id, nombre FROM Clientes")
        clientes = cursor.fetchall()
        cursor.execute("SELECT empleado_id, nombre FROM Empleados")
        empleados = cursor.fetchall()
        cursor.execute("SELECT ruta_id, descripcion FROM Rutas")
        rutas = cursor.fetchall()
        cursor.execute("SELECT vehiculo_id, placa FROM Vehículos")
        vehiculos = cursor.fetchall()
        cursor.execute("SELECT tipo_basura_id, descripcion FROM Tipos_de_Basura")
        tipos_basura = cursor.fetchall()

        cursor.close()
        conn.close()

        return JsonResponse({
            'recolecciones': recolecciones,
            'clientes': [{'id': c[0], 'nombre': c[1]} for c in clientes],
            'empleados': [{'id': e[0], 'nombre': e[1]} for e in empleados],
            'rutas': [{'id': r[0], 'descripcion': r[1]} for r in rutas],
            'vehiculos': [{'id': v[0], 'placa': v[1]} for v in vehiculos],
            'tipos_basura': [{'id': t[0], 'descripcion': t[1]} for t in tipos_basura],
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            cursor.execute("""
                INSERT INTO Recogidas (cliente_id, empleado_id, ruta_id, vehiculo_id, tipo_basura_id, fecha, hora, cantidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['cliente_id'], data['empleado_id'], data['ruta_id'], data['vehiculo_id'], data['tipo_basura_id'], data['fecha'], data['hora'], data['cantidad']))
            conn.commit()

            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest()

@login_required
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def recoleccion_detalle(request, id):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()

    if request.method == "GET":
        # Fetch a specific recoleccion
        cursor.execute("""
SELECT rec.recogida_id, CLI.nombre, emp.nombre, rut.descripcion, vehi.placa,tip.descripcion,rec.fecha,rec.hora,rec.cantidad

FROM Recogidas rec INNER JOIN Clientes CLI ON CLI.cliente_id = rec.cliente_id
inner join Empleados emp on emp.empleado_id = rec.empleado_id
inner join Rutas rut on rec.ruta_id = rut.ruta_id
inner join Vehículos vehi on rec.vehiculo_id = vehi.vehiculo_id
inner join Tipos_de_Basura tip on rec.tipo_basura_id = tip.tipo_basura_id

            WHERE recogida_id = ?
        """, (id,))
        row = cursor.fetchone()

        if row:
            recoleccion = {
                'id': row[0],
                'cliente_id': row[1],
                'empleado_id': row[2],
                'ruta_id': row[3],
                'vehiculo_id': row[4],
                'tipo_basura_id': row[5],
                'fecha': row[6],
                'hora': row[7],
                'cantidad': row[8],
            }
            cursor.close()
            conn.close()

     
            return JsonResponse(recoleccion)
        else:
            cursor.close()
            conn.close()
            return JsonResponse({'error': 'Recoleccion not found'}, status=404)

    elif request.method == "PUT":
        try:
            data = json.loads(request.body.decode('utf-8'))
            cursor.execute("""
                UPDATE Recogidas
                SET cliente_id=?, empleado_id=?, ruta_id=?, vehiculo_id=?, tipo_basura_id=?, fecha=?, hora=?, cantidad=?
                WHERE recogida_id=?
            """, (data['cliente_id'], data['empleado_id'], data['ruta_id'], data['vehiculo_id'], data['tipo_basura_id'], data['fecha'], data['hora'], data['cantidad'], id))
            conn.commit()

            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "DELETE":
        try:
            cursor.execute("DELETE FROM Recogidas WHERE recogida_id = ?", (id,))
            conn.commit()

            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest()



#Clientes

def clientes(request):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("SELECT * from Clientes")
    rows = cursor.fetchall()


    clientes = []
    for row in rows:
        clientes.append({
          'id': row[0],
                'nombre': row[1],
                'direccion' : row[2],
                'telefono': row[3],
                'email': row[4]
        })

 
    cursor.close()
    conn.close()

    return JsonResponse({'clientes': clientes})



@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def clientes_detalle(request, cliente_id=None):
    if request.method == "GET" and cliente_id:
        conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE cliente_id=?", (cliente_id,))
        row = cursor.fetchone()
        if row:
            clientes = {
                'id': row[0],
                  'nombre': row[1],
                'direccion' : row[2],
                'telefono': row[3],
                'email': row[4]
            }
            cursor.close()
            conn.close()
            return JsonResponse(clientes)
        else:
            cursor.close()
            conn.close()
            return JsonResponse({'error': 'cliente no encontrado'}, status=404)

    elif request.method == "POST":
        
        try:
            data = json.loads(request.body.decode('utf-8'))
            nombre = data.get('nombre')
            direccion = data.get('direccion')
            telefono = data.get('telefono')
            email = data.get('email')
           

            if not all([nombre, direccion, telefono,email]):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nombre, direccion, telefono,email)
                VALUES (?, ?, ?, ?)
            """, (nombre, direccion, telefono,email))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "PUT" and cliente_id:
        
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data)
            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes
                SET nombre=?, direccion=?, telefono=?,email=?
                WHERE cliente_id=?
            """, (data['nombre'], data['direccion'],data['telefono'],data['email'], cliente_id))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest()

def cotizaciones(request):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("""    SELECT co.cotizacion_id, emp.nombre, cli.nombre,co.fecha,co.total,co.estado, tip.descripcion,cruce_costos, inv.descripcion,co.cantidad from Cotizaciones as co inner join Clientes cli on cli.cliente_id = co.cliente_id
inner join Empleados emp on emp.empleado_id = co.empleado_id
inner join tipos_de_cotizacion tip on tip.tipo_cotizacion_id = co.tipo_cotizacion_id
inner join inventarioMateriales inv on co.material_id = inv.MaterialID""")
    rows = cursor.fetchall()

    cotizaciones = []
    for row in rows:
        cotizaciones.append({
            'id': row[0],
            'empleado': row[1],
            'cliente': row[2],
            'fecha': row[3],
            'total': row[4],
            'estado': row[5],
            'tip_cotizacion':row[6],
            'cruce':row[7],
            'material' : row[8],
            'cantidad':row[9]
        })

    cursor.close()
    conn.close()

    return JsonResponse({'cotizaciones': cotizaciones})


def obtener_datos_formulario():
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()
    
    cursor.execute("SELECT cliente_id, nombre FROM Clientes")
    clientes = cursor.fetchall()
    
    cursor.execute("SELECT empleado_id, nombre FROM Empleados")
    empleados = cursor.fetchall()

    cursor.execute("SELECT tipo_cotizacion_id, descripcion FROM Tipos_de_Cotizacion")
    tipos_cotizacion = cursor.fetchall()

    cursor.execute("SELECT MaterialID, NombreMaterial, CantidadDisponible FROM InventarioMateriales")
    inventarios = cursor.fetchall()
    
    cursor.close()
    conn.close()

    clientes_list = [{'cliente_id': cliente[0], 'nombre': cliente[1]} for cliente in clientes]
    empleados_list = [{'empleado_id': empleado[0], 'nombre': empleado[1]} for empleado in empleados]
    tipos_cotizacion_list = [{'tipo_cotizacion_id': tipo[0], 'descripcion': tipo[1]} for tipo in tipos_cotizacion]
    inventario_list = [{'MaterialID': inventario[0], 'descripcion': inventario[1], 'cantidad_disponible': inventario[2]} for inventario in inventarios]

    return {'clientes': clientes_list, 'empleados': empleados_list, 'tipos_cotizacion': tipos_cotizacion_list, 'inventario_list': inventario_list}


@login_required
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def cotizacion_detalle(request, cotizacion_id=None):
    if request.method == "GET" and cotizacion_id:
        conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cotizaciones WHERE cotizacion_id=?", (cotizacion_id,))
        row = cursor.fetchone()
        if row:
            cotizacion = {
                'id': row[0],
                'cliente_id': row[1],
                'empleado_id': row[2],
                'fecha': row[3],
                'total': row[4],
                'estado': row[5],
                'tipo_cotizacion_id': row[6],
                'cruce_costos': row[7],
                'msterial_id': row[8],
                'cantidad':row[9]
            }
            cursor.close()
            conn.close()
            print(cotizacion)
            return JsonResponse(cotizacion)
        else:
            cursor.close()
            conn.close()
            return JsonResponse({'error': 'Cotización no encontrada'}, status=404)

    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            cliente_id = data.get('cliente_id')
            empleado_id = data.get('empleado_id')
            material_id = data.get('material_id')
            cantidad_solicitada = data.get('cantidad_solicitada')
            fecha = data.get('fecha')
            total = data.get('total')
            estado = data.get('estado')
            tipo_cotizacion_id = data.get('tipo_cotizacion_id')
            cruce_costos = data.get('cruce_costos')

            if not all([cliente_id, empleado_id, material_id, cantidad_solicitada, fecha, total, estado, tipo_cotizacion_id]):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Cotizaciones (cliente_id, empleado_id, material_id, cantidad, fecha, total, estado, tipo_cotizacion_id, cruce_costos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cliente_id, empleado_id, material_id, cantidad_solicitada, fecha, total, estado, tipo_cotizacion_id, cruce_costos))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "PUT" and cotizacion_id:
        try:
            data = json.loads(request.body.decode('utf-8'))
            cliente_id = data.get('cliente_id')
            empleado_id = data.get('empleado_id')
            material_id = data.get('material_id')
            cantidad_solicitada = data.get('cantidad_solicitada')
            fecha = data.get('fecha')
            total = data.get('total')
            estado = data.get('estado')
            tipo_cotizacion_id = data.get('tipo_cotizacion_id')
            cruce_costos = data.get('cruce_costos')

            if not all([cliente_id, empleado_id, material_id, cantidad_solicitada, fecha, total, estado, tipo_cotizacion_id]):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Cotizaciones
                SET cliente_id=?, empleado_id=?, material_id=?, cantidad=?, fecha=?, total=?, estado=?, tipo_cotizacion_id=?, cruce_costos=?
                WHERE cotizacion_id=?
            """, (cliente_id, empleado_id, material_id, cantidad_solicitada, fecha, total, estado, tipo_cotizacion_id, cruce_costos, cotizacion_id))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "DELETE" and cotizacion_id:
        try:
            conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Cotizaciones WHERE cotizacion_id=?", (cotizacion_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest()




def calcular_cruce_costos(tipo_cotizacion_id, total):
    # Lógica de cálculo según el tipo de cotización
    if tipo_cotizacion_id == 1:  # Aprovechables
        return total * 0.8  # Ejemplo: 80% de aprovechables
    elif tipo_cotizacion_id == 2:  # No Aprovechables
        return total * 1.2  # Ejemplo: 120% de no aprovechables
    return 0

def obtener_formulario_datos(request):
    data = obtener_datos_formulario()
    return JsonResponse(data)



def inventario(request):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("""  SELECT * from InventarioMateriales """)
    rows = cursor.fetchall()


    
    inventario = []
    for row in rows:
        inventario.append({
            'id': row[0],
            'NombreMaterial': row[1],
            'Descripcion': row[2],
            'Categoria': row[3],
            'PrecioPorUnidad': row[4],
            'CantidadDisponible': row[5],
            'UnidadMedida':row[6],
            'FechaIngreso':row[7],
            'Reciclable':row[8],
            'Vendible': row[9]
        })

    cursor.close()
    conn.close()

    return JsonResponse({'inventario': inventario})

def inventario_detalle(request, id=None):
    conn = pyodbc.connect(settings.SQL_SERVER_CONNECTION_STRING)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM InventarioMateriales WHERE MaterialID = ?", id)
        row = cursor.fetchone()
        if row:
            material = {
                'id': row[0],
                'NombreMaterial': row[1],
                'Descripcion': row[2],
                'Categoria': row[3],
                'PrecioPorUnidad': row[4],
                'CantidadDisponible': row[5],
                'UnidadMedida': row[6],
                'FechaIngreso': row[7],
                'Reciclable': row[8],
                'Vendible': row[9]
            }
            return JsonResponse(material)
        else:
            return JsonResponse({'error': 'Material no encontrado'}, status=404)

    elif request.method == 'POST':
        data = json.loads(request.body)
        cursor.execute("""
            INSERT INTO InventarioMateriales 
            (NombreMaterial, Descripcion, Categoria, PrecioPorUnidad, CantidadDisponible, UnidadMedida, Reciclable, Vendible) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            data['NombreMaterial'], data['Descripcion'], data['Categoria'], data['PrecioPorUnidad'],
            data['CantidadDisponible'], data['UnidadMedida'], data.get('Reciclable', 1), data.get('Vendible', 1)
        )
        conn.commit()
        return JsonResponse({'status': 'Material creado'}, status=201)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        cursor.execute("""
            UPDATE InventarioMateriales SET 
            NombreMaterial = ?, Descripcion = ?, Categoria = ?, PrecioPorUnidad = ?, CantidadDisponible = ?, UnidadMedida = ?, Reciclable = ?, Vendible = ?
            WHERE MaterialID = ?
            """,
            data['NombreMaterial'], data['Descripcion'], data['Categoria'], data['PrecioPorUnidad'],
            data['CantidadDisponible'], data['UnidadMedida'], data.get('Reciclable', 1), data.get('Vendible', 1), id
        )
        conn.commit()
        return JsonResponse({'status': 'Material actualizado'})

    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM InventarioMateriales WHERE MaterialID = ?", id)
        conn.commit()
        return JsonResponse({'status': 'Material eliminado'})

    cursor.close()
    conn.close()
    return JsonResponse({'error': 'Método no permitido'}, status=405)