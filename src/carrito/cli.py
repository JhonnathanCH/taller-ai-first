"""Línea de comandos del carrito."""

import argparse
from collections.abc import Collection, Iterable

from carrito.datos import pedido
from carrito.descuentos import PROMOCIONES
from carrito.precios import precio_linea
from carrito.resumen import resumen


def pesos(monto: int) -> str:
    """Separador de miles chileno: 49400 -> '49.400'."""
    return f"{monto:,}".replace(",", ".")


def columna_pesos(montos: Iterable[int], ancho: int = 0) -> list[str]:
    """Pesos con el `$` alineado: [49400, 9386] -> ['$ 49.400', '$  9.386'].

    `ancho` fuerza el ancho de las cifras, para alinear el `$` entre varias tablas.
    """
    cifras = list(map(pesos, montos))
    ancho = max([ancho, *map(len, cifras)])
    return [f"$ {cifra:>{ancho}}" for cifra in cifras]


def anchos_de(encabezado: list[str], filas: list[list[str]]) -> list[int]:
    """Ancho natural de cada columna: el texto más largo entre encabezado y filas."""
    return [max(map(len, columna)) for columna in zip(encabezado, *filas, strict=True)]


def tabla(
    encabezado: list[str],
    filas: list[list[str]],
    alinear_derecha: Collection[int] = (),
    anchos: list[int] | None = None,
) -> str:
    """Tabla ASCII con bordes. Las columnas en `alinear_derecha` se alinean a la derecha.

    `anchos` permite forzar el ancho de cada columna, para alinear varias tablas entre sí.
    """
    anchos = anchos or anchos_de(encabezado, filas)
    borde = "+" + "+".join("-" * (ancho + 2) for ancho in anchos) + "+"

    def render(fila: list[str]) -> str:
        celdas = (
            celda.rjust(anchos[i]) if i in alinear_derecha else celda.ljust(anchos[i])
            for i, celda in enumerate(fila)
        )
        return "| " + " | ".join(celdas) + " |"

    return "\n".join([borde, render(encabezado), borde, *map(render, filas), borde])


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    parser.add_argument("--sin", action="append", choices=sorted(PROMOCIONES), default=[])
    parser.add_argument("--detalle", action="store_true")
    args = parser.parse_args()

    try:
        elegido = pedido(args.pedido)
    except KeyError:
        parser.error(f"el pedido {args.pedido} no existe")
    elegido.promociones = [p for p in elegido.promociones if p not in args.sin]
    desglose = resumen(elegido)
    montos_lineas = [precio_linea(linea) for linea in elegido.lineas] if args.detalle else []
    ancho_cifras = max(len(pesos(monto)) for monto in [*desglose.values(), *montos_lineas])

    encabezado_resumen = ["Concepto", "Monto"]
    filas_resumen = [
        [concepto, monto]
        for concepto, monto in zip(desglose, columna_pesos(desglose.values(), ancho_cifras))
    ]
    anchos_resumen = anchos_de(encabezado_resumen, filas_resumen)

    if args.detalle:
        encabezado_detalle = ["Producto", "Cantidad", "Monto"]
        filas_detalle = [
            [linea.producto.nombre, str(linea.cantidad), monto]
            for linea, monto in zip(elegido.lineas, columna_pesos(montos_lineas, ancho_cifras))
        ]
        anchos_detalle = anchos_de(encabezado_detalle, filas_detalle)

        # Ambas tablas comparten la columna Monto y el ancho total:
        # Concepto ocupa lo mismo que Producto + Cantidad (más el separador " | ").
        producto, cantidad, monto = anchos_detalle
        concepto = max(anchos_resumen[0], producto + cantidad + 3)
        producto = concepto - cantidad - 3
        print(tabla(encabezado_detalle, filas_detalle, alinear_derecha={1, 2}, anchos=[producto, cantidad, monto]))
        print()
        anchos_resumen = [concepto, monto]

    print(tabla(encabezado_resumen, filas_resumen, alinear_derecha={1}, anchos=anchos_resumen))


if __name__ == "__main__":
    main()
