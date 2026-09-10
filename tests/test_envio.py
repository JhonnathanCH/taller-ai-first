"""Steps de pytest-bdd para tests/features/envio.feature."""

from pytest_bdd import given, parsers, scenarios, then, when

from carrito.descuentos import total_con_descuentos
from carrito.modelo import Cupon, Linea, Pedido, Producto
from carrito.resumen import resumen

scenarios("features/envio.feature")


def _a_entero(monto_con_puntos: str) -> int:
    return int(monto_con_puntos.replace(".", ""))


def _pedido_de_un_producto(monto: str, region: str, cantidad: int = 1) -> Pedido:
    producto = Producto(sku="SKU-1", nombre="Producto de prueba", precio=_a_entero(monto))
    return Pedido(numero=1, lineas=[Linea(producto=producto, cantidad=cantidad)], region=region)


@given(
    parsers.re(
        r'un pedido sin cupones ni promociones, con un solo producto de '
        r'\$(?P<monto>[\d.]+) en la región "(?P<region>\w+)"'
    ),
    target_fixture="pedido",
)
def _dado_pedido_sin_descuentos(monto: str, region: str) -> Pedido:
    return _pedido_de_un_producto(monto, region)


@given(
    parsers.re(
        r'un pedido con un solo producto de \$(?P<monto>[\d.]+) '
        r'en cantidad (?P<cantidad>\d+) en la región "(?P<region>\w+)"'
    ),
    target_fixture="pedido",
)
def _dado_pedido_con_cantidad(monto: str, cantidad: str, region: str) -> Pedido:
    return _pedido_de_un_producto(monto, region, cantidad=int(cantidad))


@given(
    parsers.re(
        r'un pedido con un solo producto de \$(?P<monto>[\d.]+) en la región "(?P<region>\w+)"'
    ),
    target_fixture="pedido",
)
def _dado_pedido_simple(monto: str, region: str) -> Pedido:
    return _pedido_de_un_producto(monto, region)


@given("la clienta no es nueva")
def _clienta_no_es_nueva(pedido: Pedido) -> None:
    pedido.cliente_nuevo = False


@given("la clienta es nueva")
def _clienta_es_nueva(pedido: Pedido) -> None:
    pedido.cliente_nuevo = True


@given(parsers.re(r'el pedido tiene un cupón de monto fijo por \$(?P<monto>[\d.]+)'))
def _agregar_cupon_de_monto(pedido: Pedido, monto: str) -> None:
    pedido.cupones.append(Cupon(codigo="CUPON-TEST", tipo="monto", valor=_a_entero(monto)))


@given(parsers.parse('el pedido tiene la promoción "{nombre}"'))
def _agregar_promocion(pedido: Pedido, nombre: str) -> None:
    pedido.promociones.append(nombre)


@when("calculo el resumen del pedido", target_fixture="resultado")
def _calcular_resumen(pedido: Pedido) -> dict:
    return {
        "lineas": resumen(pedido),
        "descontado": total_con_descuentos(pedido),
    }


@then(parsers.re(r'el envío cobrado es \$(?P<valor>[\d.]+)'))
def _verificar_envio(resultado: dict, valor: str) -> None:
    assert resultado["lineas"]["Envío"] == _a_entero(valor)


@then(parsers.re(r'el monto descontado es \$(?P<valor>[\d.]+)'))
def _verificar_monto_descontado(resultado: dict, valor: str) -> None:
    assert resultado["descontado"] == _a_entero(valor)


@then(parsers.re(r'el IVA es \$(?P<valor>[\d.]+)'))
def _verificar_iva(resultado: dict, valor: str) -> None:
    assert resultado["lineas"]["IVA"] == _a_entero(valor)


@then(parsers.re(r'el monto con IVA incluido sería \$(?P<valor>[\d.]+)'))
def _verificar_monto_con_iva(resultado: dict, valor: str) -> None:
    assert resultado["descontado"] + resultado["lineas"]["IVA"] == _a_entero(valor)
