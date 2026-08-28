"""Política de descuentos: cupones porcentuales antes que vales de monto fijo."""

from carrito.descuentos import total_con_descuentos
from carrito.modelo import Cupon, Linea, Pedido, Producto


def test_cupon_porcentual_se_aplica_antes_que_vale_de_monto_fijo():
    # Subtotal redondo: 1 x $10.000.
    producto = Producto(sku="A1", nombre="Producto", precio=10_000)
    pedido = Pedido(
        numero=1,
        lineas=[Linea(producto=producto, cantidad=1)],
        cupones=[
            # El vale va primero en la lista a propósito: la política manda,
            # no el orden de entrada.
            Cupon(codigo="VALE2000", tipo="monto", valor=2_000),
            Cupon(codigo="DIEZ", tipo="porcentaje", valor=10),
        ],
    )

    # Según README y docstring de carrito.descuentos:
    #   10.000 - 10% = 9.000, luego 9.000 - 2.000 = 7.000.
    # En el orden inverso daría 10.000 - 2.000 = 8.000, luego -10% = 7.200.
    assert total_con_descuentos(pedido) == 7_000
