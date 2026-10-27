import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import Producto, Stock, DetalleVenta,Venta
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.
# Request Login (NO lleva decorador para permitir el ingreso)
def login_pagina(request):
    return render(request, 'Negocioapp/login.html')

# Request Cerrar Sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('login_pagina')

# Request de inicio
@login_required
def inicio(request):
    return render(request, 'Negocioapp/inicio.html')

# Request de Producto
@login_required
def productos(request):
    return render(request, 'Negocioapp/productos.html')
    
@login_required
def crear_producto(request):
    return render(request, 'Negocioapp/crear_producto.html')

@login_required
def editar_producto(request, id):
    return render(request, 'Negocioapp/editar_producto.html', {'producto_id': id})

@login_required
def detalle_producto(request, id):
    return render(request, 'Negocioapp/detalle_producto.html', {'producto_id': id})

@login_required
def elimar_producto(request, id):
    return render(request, 'Negocioapp/eliminar_producto.html', {'producto_id': id})

# Request de Stock
@login_required
def ver_stock(request):
    return render(request, 'Negocioapp/ver_stock.html')

@login_required
def editar_stock(request, pk):
    return render(request, 'Negocioapp/editar_stock.html', {'stock_id': pk})

# Request Venta
@login_required
def ventas(request):
    return render(request, 'Negocioapp/ventas.html')

@login_required
def crear_venta(request):
    return render(request, 'Negocioapp/crear_venta.html')

@login_required
def detalle_venta(request, venta_id):
    return render(request, 'Negocioapp/detalle_venta.html', {'venta_id': venta_id})

# Request de Conversor

@login_required
def resumen_venta(request):
    return render(request, 'Negocioapp/resumen_venta.html')

@login_required
def historial_venta(request):
    return render(request, 'Negocioapp/historial_venta.html')


#API'S
class LoginApiView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Recibir las credenciales de JSON
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Validar credenciales de usuario (añade request como primer argumento)
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            # 2. ESTA ES LA CLAVE: Crea la sesión tradicional en el navegador
            login(request, usuario)

            # 3. Mantienes tu Token intacto para tu API / JavaScript
            token, creado = Token.objects.get_or_create(user=usuario)

            return Response({
                'mensaje': 'Autenticacion correcta',
                'usuario': usuario.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
            
        return Response({
            'error': 'Usuario o contraseña incorrecta'
        }, status=status.HTTP_401_UNAUTHORIZED)

class ProductoApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    

    def get(self,request):#Ver todos los productos por medio de un array llamado datos con get 

        productos = Producto.objects.filter(estado=True)

        datos = []

        for producto in productos:
            datos.append({

            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria,
            'fecha_caducidad': producto.fecha_caducidad,
            'fecha_registro': producto.fecha_registro,
            'precio_compra': producto.precio_compra,
            'precio_venta': producto.precio_venta,
            'estado': producto.estado, # Este es para dar de baja un producto que no se considere sin romper el historial de la BD
            'imagen': producto.imagen.url if producto.imagen else None

            })
        return Response(datos, status=status.HTTP_200_OK)

    def post(self,request):# Crear Un producto funcion del post 

        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion')
        categoria = request.data.get('categoria')
        fecha_caducidad= request.data.get('fecha_caducidad')
        fecha_registro = request.data.get('fecha_registro')
        precio_compra = int(request.data.get('precio_compra'))
        precio_venta = int(request.data.get('precio_venta'))
        estado = request.data.get('estado')

        imagen = request.FILES.get('imagen')
        

        if not nombre or not descripcion or not categoria or not fecha_registro or precio_compra is None or  precio_venta is None or estado is None:

            return Response({
                'error': 'Ningun campo puede estar vacio, son obligatorios'
            }, status=status.HTTP_400_BAD_REQUEST)

        if precio_compra <= 0 or precio_venta <= 0:
            return Response({
                'error': 'Los campos precio de compra y de venta no pueden ser negativos'
            }, status=status.HTTP_400_BAD_REQUEST)            

        if Producto.objects.filter(nombre__iexact=nombre).exists():
            return Response({
                'error': 'No pueden existir productos con el mismo nombre, utiliza otro nombre '
            },status=status.HTTP_400_BAD_REQUEST)

        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            fecha_caducidad = fecha_caducidad if fecha_caducidad else None,
            fecha_registro=fecha_registro,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            estado=estado,
            imagen=imagen,
            
        )

        stock_actual = request.data.get('stock_actual')
        stock_minimo = request.data.get('stock_minimo')

        if not stock_actual or not stock_minimo:
            return Response({
                'mensaje': 'Stock mimino y actual no puede estar vacio'
            }, status=status.HTTP_400_BAD_REQUEST)

        stock_actual = int(stock_actual)
        stock_minimo = int(stock_minimo)
        
        if stock_minimo< 1 or stock_actual < 0:
            return Response({
                'mensaje': 'El stock minimo no puede ser negativo y el stock actual debe ser 0 o mayor a 1'
            }, status=status.HTTP_400_BAD_REQUEST)
        Stock.objects.create(
                producto=producto,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
            ) 
       
        return Response({
            'mesaje': 'Producto ingresado',
            'producto':{
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'categoria': producto.categoria,
                'fecha_caducidad': producto.fecha_caducidad,
                'fecha_registro': producto.fecha_registro,
                'precio_compra': producto.precio_compra,
                'precio_venta': producto.precio_venta,
                'estado': producto.estado,
                'imagen': producto.imagen.url if producto.imagen else None
            }
        },status=status.HTTP_201_CREATED)

class ProductoDetallApiView(APIView):
    authentication_classes= [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):

        producto = get_object_or_404(Producto,id=id)

        return Response({

            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria,
            'fecha_caducidad': producto.fecha_caducidad,
            'fecha_registro': producto.fecha_registro,
            'precio_compra': producto.precio_compra,
            'precio_venta': producto.precio_venta,
            'estado': producto.estado,
            'imagen': producto.imagen.url if producto.imagen else None
        })

    def put(self, request, id):

        producto = get_object_or_404(Producto, id=id)

        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion')
        categoria = request.data.get('categoria')
        fecha_caducidad= request.data.get('fecha_caducidad')
        fecha_registro = request.data.get('fecha_registro')
        precio_compra = request.data.get('precio_compra')
        precio_venta = request.data.get('precio_venta')
        estado = request.data.get('estado')

        imagen = request.FILES.get('imagen')

        if not nombre or not descripcion or not categoria or not fecha_registro or precio_compra is None  or precio_venta is None or estado is None:
    
                return Response({
                    'error': 'Ningun campo puede estar vacio, son obligatorios'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if precio_compra < 0 or precio_venta < 0:
            return Response({
                'error': 'Los campos precio de compra y de venta no pueden ser negativos'
            }, status=status.HTTP_400_BAD_REQUEST)            

        if Producto.objects.filter(nombre__iexact=nombre).exclude(id=producto.id).exists():
            return Response({
                'error': 'No pueden existir productos con el mismo nombre, utiliza otro nombre '
            },status=status.HTTP_400_BAD_REQUEST)
    
        producto.nombre = nombre 
        producto.descripcion=descripcion
        producto.categoria=categoria
        producto.fecha_caducidad=fecha_caducidad if fecha_caducidad else None
        producto.fecha_registro=fecha_registro
        producto.precio_compra=precio_compra
        producto.precio_venta=precio_venta
        producto.estado=estado

        if imagen:
            producto.imagen = imagen

        producto.save()
        return Response({
            'mesaje': 'Producto actualizado',
            'producto':{
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'categoria': producto.categoria,
                'fecha_caducidad': producto.fecha_caducidad,
                'fecha_registro': producto.fecha_registro,
                'precio_compra': producto.precio_compra,
                'precio_venta': producto.precio_venta,
                'estado': producto.estado,
                'imagen': producto.imagen.url if producto.imagen else None
            }
        },status=status.HTTP_200_OK)

    def patch(self, request, id):

        producto = get_object_or_404(Producto, id=id)

        nombre = request.data.get('nombre', producto.nombre)
        descripcion = request.data.get('descripcion', producto.descripcion)
        categoria = request.data.get('categoria',producto.categoria)
        fecha_caducidad= request.data.get('fecha_caducidad',producto.fecha_caducidad)
        fecha_registro = request.data.get('fecha_registro',producto.fecha_registro)
        precio_compra = int(request.data.get('precio_compra',producto.precio_compra))
        precio_venta = int(request.data.get('precio_venta',producto.precio_venta))
        estado = request.data.get('estado',producto.estado)

        imagen = request.FILES.get('imagen')
        
        if not nombre or not descripcion or not categoria or not fecha_registro or precio_compra is None  or precio_venta is None or estado is None:
                return Response({
                    'error': 'Ningun campo puede estar vacio, son obligatorios'
                }, status=status.HTTP_400_BAD_REQUEST)

        if precio_compra <= 0 or precio_venta <= 0:
            return Response({
                'error': 'Los campos precio de compra y de venta no pueden ser negativos'
            }, status=status.HTTP_400_BAD_REQUEST)            

        if Producto.objects.filter(nombre__iexact=nombre).exclude(id=producto.id).exists():
            return Response({
                'error': 'No pueden existir productos con el mismo nombre, utiliza otro nombre '
            },status=status.HTTP_400_BAD_REQUEST)
    

        producto.nombre = nombre 
        producto.descripcion=descripcion
        producto.categoria=categoria
        producto.fecha_caducidad=fecha_caducidad if fecha_caducidad else None
        producto.fecha_registro=fecha_registro
        producto.precio_compra=precio_compra
        producto.precio_venta=precio_venta
        producto.estado=estado

        if imagen:
            producto.imagen = imagen

        producto.save()
        return Response({
            'mesaje': 'Producto actualizado',
            'producto':{
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'categoria': producto.categoria,
                'fecha_caducidad': producto.fecha_caducidad,
                'fecha_registro': producto.fecha_registro,
                'precio_compra': producto.precio_compra,
                'precio_venta': producto.precio_venta,
                'estado': producto.estado,
                'imagen': producto.imagen.url if producto.imagen else None
            }
        },status=status.HTTP_200_OK)

    def delete(self,request, id):

        producto = get_object_or_404(Producto, id=id)
        producto.estado = False
        producto.save()
        return Response({'mensaje':'Producto Eliminado'},status=status.HTTP_200_OK)
        
class StockApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):

        stocks = Stock.objects.filter(producto__estado=True)

        datos1= []

        for stock in stocks:
            datos1.append({
                'id': stock.id,                           
                'producto': stock.producto_id,            
                'producto_nombre': stock.producto.nombre, 
                'stock_actual': stock.stock_actual,
                'stock_minimo': stock.stock_minimo,
                'imagen': stock.producto.imagen.url if stock.producto.imagen else None
            })

        return Response(datos1, status=status.HTTP_200_OK)


# ver todo el stock y actualizar

class StockDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        data = {
            'id': stock.id,
            'producto': stock.producto_id,
            'producto_nombre': stock.producto.nombre,
            'stock_actual': stock.stock_actual,
            'stock_minimo': stock.stock_minimo,
            'imagen': stock.producto.imagen.url if stock.producto.imagen else None
        }
        return Response(data, status=status.HTTP_200_OK)
    
    def put(self,request,pk):
        try:
            stock = Stock.objects.get(pk=pk)

            stock_actual = request.data.get('stock_actual')
            stock_minimo = request.data.get('stock_minimo')

            if not stock_actual or not stock_minimo:
                return Response({
                    'mensaje': 'En la actualizacion del producto en stock los valores no pueden ser negativos ni mejores a cero'
                },status=status.HTTP_400_BAD_REQUEST)

            stock_actual, stock_minimo = int(stock_actual), int(stock_minimo)
              
            if stock_minimo< 1 or stock_actual < 0:
                return Response({
                    'mensaje': 'El stock minimo no puede ser negativo y el stock actual debe ser 0 o mayor a 1'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            stock.stock_actual=stock_actual
            stock.stock_minimo=stock_minimo
            stock.save()

            return Response({
                'mensaje': 'Stock actualizado correctamente'
            }, status=status.HTTP_200_OK)

        except Stock.DoesNotExist:
            return Response({
                'mensaje': 'No hay producto asi guardado en stock',
            }, status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,pk):

        try:
            stock = Stock.objects.get(pk=pk)
            stock_actual = request.data.get('stock_actual')
            if stock_actual is None:
                stock_actual = int(stock_actual)
                if stock_actual < 0:
                    return Response({
                        'mensaje':'El stock actual no debe ser negativo puede ser 0 o mayor a este'
                    }, status=status.HTTP_400_BAD_REQUEST)
            stock.stock_actual
            stock_minimo = request.data.get('stock_minimo')
            if stock_minimo is None:
                stock_minimo = int(stock_minimo)
                if stock_minimo < 1:
                    return Response({
                        'mensaje':'El stock minimo no debe ser negativo'
                    }, status=status.HTTP_400_BAD_REQUEST)
            stock.stock_minimo
            stock.save()

            return Response({
                'mensaje': 'Campo del Stock actualizado correctamente'
            }, status=status.HTTP_200_OK)
        
        except Stock.DoesNotExist:
            return Response({
                'mensaje': 'No hay producto asi guardado en stock'
            }, status=status.HTTP_404_NOT_FOUND)
          

class VentaApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        ventas = Venta.objects.all()
        datos2 = []

        for venta in ventas:
            detalles = DetalleVenta.objects.filter(venta=venta)
            detalles_data = [{
                'producto_id': detalle.producto.id,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario)
            } for detalle in detalles]

            datos2.append({
                'id': venta.id,
                'fecha_venta': venta.fecha_venta,
                'vendedor': venta.vendedor.username,
                'estado': venta.estado,
                'metodo_pago': venta.metodo_pago,
                'total': float(venta.total),
                'detalles': detalles_data
            })
        
        return Response(datos2, status=status.HTTP_200_OK)

    def post(self, request):
        fecha_venta = request.data.get('fecha_venta')
        estado = request.data.get('estado')
        metodo_pago = request.data.get('metodo_pago')
        total = request.data.get('total')
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad')
        precio_unitario = request.data.get('precio_unitario')
        
        vendedor = request.user

        # Verificamos que ningún campo llegue vacío (usando is not None para los números por si vienen en 0)
        if not fecha_venta or not vendedor or not estado or not metodo_pago or total is None or not producto_id or not cantidad or precio_unitario is None:
            return Response({
                'error': 'Ningun campo puede estar vacio al crear venta'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = float(total)
            cantidad = int(cantidad)
            producto_id = int(producto_id)
            precio_unitario = float(precio_unitario)
        except (ValueError, TypeError):
            return Response({
                'error': 'Los formatos de los valores numéricos no son válidos'
            }, status=status.HTTP_400_BAD_REQUEST)

        if total <= 0 or cantidad <= 0 or precio_unitario <= 0:
            return Response({
                'mensaje': 'Los valores numéricos deben ser mayores a 0'
            }, status=status.HTTP_400_BAD_REQUEST) 

        try:
            # Buscamos el stock utilizando el ID del producto
            stock = Stock.objects.get(producto_id=producto_id)

            if stock.stock_actual < cantidad:
                return Response({
                    'mensaje': 'No hay suficiente stock disponible para este producto'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Transacción atómica para asegurar consistencia entre stock, venta y detalle
            with transaction.atomic():
                # 1. Descontamos el stock actual
                stock.stock_actual -= cantidad
                stock.save()

                # 2. Creamos la venta principal
                venta = Venta.objects.create(
                    fecha_venta=fecha_venta,
                    vendedor=vendedor,
                    estado=estado,
                    metodo_pago=metodo_pago,
                    total=total,
                )

                # 3. Creamos el detalle de la venta asociando el producto
                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=stock.producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )

            return Response({
                'mensaje': 'Venta ingresada y stock actualizado con éxito',
                'venta_id': venta.id,
                'detalle_id': detalle.id,
                'total': float(venta.total)
            }, status=status.HTTP_201_CREATED)

        except Stock.DoesNotExist:
            return Response({
                'mensaje': 'El producto no cuenta con un registro de stock en el inventario'
            }, status=status.HTTP_404_NOT_FOUND)
   
class DetalleventApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, venta_id):
        try:
            venta = Venta.objects.get(pk=venta_id)
        except Venta.DoesNotExist:
            return Response({
                'mensaje': 'La venta solicitada no existe'
            }, status=status.HTTP_404_NOT_FOUND)

        detalle = DetalleVenta.objects.filter(venta=venta)
        
        detalle_data = [{
            'producto_id': item.producto.id,
            'cantidad': item.cantidad,
            'precio_unitario': float(item.precio_unitario)
        } for item in detalle]

        return Response({
            'id': venta.id,
            'fecha_venta': venta.fecha_venta,
            'vendedor': venta.vendedor.username,
            'estado': venta.estado,
            'metodo_pago': venta.metodo_pago,
            'total': float(venta.total),
            'detalles': detalle_data
        }, status=status.HTTP_200_OK)

class ResumenVentasDiaApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ahora_local = timezone.localtime(timezone.now())
        hoy_local = ahora_local.date()

        inicio_dia = timezone.make_aware(timezone.datetime.combine(hoy_local, timezone.datetime.min.time()))
        fin_dia = timezone.make_aware(timezone.datetime.combine(hoy_local, timezone.datetime.max.time()))

        # Obtener IDs de ventas que contienen algún producto inactivo para excluirlas de forma limpia
        ventas_inactivas_ids = DetalleVenta.objects.filter(producto__estado=False).values_list('venta_id', flat=True)

        ventas_hoy = Venta.objects.filter(
            fecha_venta__gte=inicio_dia, 
            fecha_venta__lte=fin_dia
        ).exclude(id__in=ventas_inactivas_ids)

        cantidad_ventas = ventas_hoy.count()
        resultado_suma = ventas_hoy.aggregate(total_recaudado=Sum('total'))
        total_base = float(resultado_suma['total_recaudado'] or 0.0)

        # Capturar parámetros del conversor libre
        moneda_origen = request.GET.get('from', 'CLP').upper()
        moneda_destino = request.GET.get('to', 'USD').upper()
        
        monto_param = request.GET.get('amount')
        monto_a_convertir = float(monto_param) if monto_param else total_base

        total_convertido = monto_a_convertir
        tasa_cambio = 1.0
        error_api = None

        # Petición a la API en tiempo real con calibración opcional
        if monto_a_convertir > 0 and moneda_origen != moneda_destino:
            url = f"https://api.exchangerate-api.com/v4/latest/{moneda_origen}"
            try:
                response = requests.get(url, timeout=5)
                data = response.json()

                if response.status_code == 200 and 'rates' in data:
                    rates = data['rates']
                    if moneda_destino in rates:
                        tasa_cambio = float(rates[moneda_destino])
                        total_convertido = monto_a_convertir * tasa_cambio
                        
                        # --- CALIBRACIÓN DE LECTURA ---
                        par_monedas = f"{moneda_origen}_{moneda_destino}"
                        factores_calibracion = {
                            'ARS_CLP': 1.0107,
                        }
                        
                        if par_monedas in factores_calibracion:
                            tasa_cambio = tasa_cambio * factores_calibracion[par_monedas]
                            total_convertido = monto_a_convertir * tasa_cambio
                        # -----------------------------

                    else:
                        error_api = f"La moneda destino {moneda_destino} no está disponible."
                else:
                    error_api = "No se pudo conectar con el servicio de divisas."
            except Exception as e:
                error_api = str(e)
        elif moneda_origen == moneda_destino:
            total_convertido = monto_a_convertir

        return Response({
            'fecha': str(hoy_local),
            'cantidad_ventas_hoy': cantidad_ventas,
            'total_base': total_base,
            'error_api': error_api,
            'conversion': {
                'moneda_origen': moneda_origen,
                'moneda_destino': moneda_destino,
                'tasa_cambio': tasa_cambio,
                'total_convertido': total_convertido
            }
        }, status=status.HTTP_200_OK)


class HistorialVentasApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Usamos el mismo criterio limpio de exclusión de ventas con productos inactivos
        ventas_inactivas_ids = DetalleVenta.objects.filter(producto__estado=False).values_list('venta_id', flat=True)

        historial = (
            Venta.objects.exclude(id__in=ventas_inactivas_ids)
            .annotate(fecha=TruncDate('fecha_venta'))
            .values('fecha')
            .annotate(
                cantidad_ventas=Count('id'),
                total_recaudado=Sum('total')
            )
            .order_by('-fecha')[:30]
        )

        data_resultado = [
            {
                'fecha': str(item['fecha']),
                'cantidad_ventas': item['cantidad_ventas'],
                'total_recaudado': float(item['total_recaudado'] or 0.0)
            }
            for item in historial
        ]

        return Response(data_resultado, status=status.HTTP_200_OK)