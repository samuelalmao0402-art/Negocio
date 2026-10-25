from django.urls import path
from . import views

urlpatterns = [
    # URLS Request (Vistas HTML)
    path('', views.login_pagina, name='login_pagina'),
    path('inicio/', views.inicio, name='inicio'),

    # URLS Producto
    path('producto/', views.productos, name='productos'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:id>/', views.elimar_producto, name='eliminar_producto'),
    path('producto/detalle/<int:id>/', views.detalle_producto, name='detalle_producto'),

    # URLS Stock
    path('stock/', views.ver_stock, name='ver_stock'),
    path('stock/editar/<int:pk>/', views.editar_stock, name='editar_stock'),

    # URLS Ventas
    path('venta/', views.ventas, name='ventas'),
    path('venta/crear/', views.crear_venta, name='crear_venta'),
    path('venta/detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),

    # URL API Login
    path('api/login/', views.LoginApiView.as_view(), name='api_login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # URLS API Producto
    path('api/producto/', views.ProductoApiView.as_view(), name='api_productos'),
    path('api/producto/<int:id>/', views.ProductoDetallApiView.as_view(), name='api_detalle_producto'),
    path('api/producto/editar/<int:id>/', views.ProductoDetallApiView.as_view(), name='api_editar_producto'),
    path('api/producto/eliminar/<int:id>/', views.ProductoDetallApiView.as_view(), name='api_eliminar_producto'),

    # URLS API Stock
    path('api/stock/', views.StockApiView.as_view(), name='api_ver_producto'),
    path('api/stock/<int:pk>/', views.StockDetalleApiView.as_view(), name='api_editar_stock'),

    # URLS API Ventas/DetalleVentas
    path('api/venta/', views.VentaApiView.as_view(), name='api_ventas'),
    path('api/detalleventa/<int:venta_id>/', views.DetalleventApiView.as_view(), name='api_detalle_venta'),
    path('api/resumen_venta/', views.ResumenVentasDiaApiView.as_view(), name='api_resumen_venta'),
    path('api/historial_ventas/', views.HistorialVentasApiView.as_view(), name='api_historial_ventas'),
]