from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    productos,
    index,
    productos_template,
    producto_detalle,
    vehiculos_template,
    vehiculos,
    vehiculos_detalle,
    recolecciones,
    recolecciones_template,
    recoleccion_detalle,
    clientes,
    clientes_detalle,
    clientes_template,
    user_login,
    registro,
    cotizaciones,
    cotizacion_detalle,
    obtener_formulario_datos,
 cotizacion_template,
 inventario,
 inventario_template,
 inventario_detalle

)

urlpatterns = [
    path('', index, name='index'),
    path('user_login/', user_login, name='user_login'),
    path('registro/',registro, name='registro'),
    path('get/productos/', productos, name='productos'),
    path('productos_template/', productos_template, name='productos_template'),
    path('productos/<int:product_id>/', producto_detalle, name='producto_detalle'),
    path('productos/', producto_detalle, name='producto_detalle'),
    path('get/vehiculos/', vehiculos, name='vehiculos'),
    path('vehiculos_template/', vehiculos_template, name='vehiculos_template'),
    path('vehiculos/<int:vehiculo_id>/', vehiculos_detalle, name='vehiculos_detalle'),
    path('vehiculos/', vehiculos_detalle, name='vehiculos_detalle'),
    path('get/recolecciones/', recolecciones, name='recolecciones'),
    path('recolecciones_template/', recolecciones_template, name='recolecciones_template'),
    path('get/recolecciones/<int:recogida_id>/', recoleccion_detalle, name='recoleccion_detalle'),

    path('get/clientes/', clientes, name='clientes'),
    path('clientes_templete/', clientes_template, name='clientes_template'),
    path('clientes/<int:cliente_id>/', clientes_detalle, name='clientes_detalle'),
    path('clientes/', clientes_detalle, name='clientes_detalle'),


    path('cotizacion_template/', cotizacion_template, name='cotizacion_template'),
    path('cotizaciones/', cotizaciones, name='cotizaciones'),
    path('cotizacion/<int:cotizacion_id>/', cotizacion_detalle, name='cotizacion_detalle'),
    path('cotizacion/', cotizacion_detalle, name='cotizacion_detalle'),
    path('obtener_formulario_datos/', obtener_formulario_datos, name='obtener_formulario_datos'),

    
    path('inventario_template/', inventario_template, name='inventario_template'),
    path('inventario/data/', inventario, name='inventario_data'),
    path('inventario/<int:id>/',inventario_detalle, name='inventario_detalle'),
    path('inventario/',inventario_detalle, name='create_inventario')
     

]
