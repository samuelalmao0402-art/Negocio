from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    T_categoria = [
            ('alimento','ALIMENTO'),
            ('higiene','HIGIENE'),
            ('ropa','ROPA'),
            ('maquillaje','MAQUILLAJE'),
            ('adornos','ADORNOS'),
            ('perfumes','PERFUMES')
        ]
    categoria = models.CharField(max_length=15, choices=T_categoria)
    fecha_caducidad = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)

class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=1)

class Venta(models.Model):
    fecha_venta = models.DateTimeField(db_index=True)
    vendedor = models.ForeignKey(User, on_delete=models.PROTECT)
    T_estado = [
        ('completada','COMPLETADA'),
        ('anulada','ANULADA')
        ]
    estado = models.CharField(max_length=15, choices=T_estado)
    T_metodo = [
        ('efectivo','EFECTIVO'),
        ('transferencia','TRANSFERENCIA')
        ]
    metodo_pago = models.CharField(max_length=15, choices=T_metodo)
    total = models.DecimalField(max_digits=30, decimal_places=2)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)




 