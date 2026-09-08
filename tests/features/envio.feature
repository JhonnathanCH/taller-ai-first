# language: es
# Reglas de negocio fijadas para esta funcionalidad (no se discuten aquí):
#   1. El umbral de $50.000 se evalúa DESPUÉS de aplicar descuentos (cupones y
#      promociones), es decir, contra el monto que devuelve
#      `descuentos.total_con_descuentos`, no contra el subtotal.
#   2. El IVA NO cuenta para el umbral: se calcula sobre el monto ya
#      descontado, pero se suma después de decidir el costo de envío.
#   3. Las promociones descuentan del monto exactamente igual que los cupones
#      a efectos del umbral (ambas reducen el monto que se compara contra
#      $50.000).
#   4. Con $50.000 justos el envío es gratis (la comparación en código es
#      `monto >= UMBRAL_ENVIO_GRATIS`).

Característica: Envío gratis por monto, región y tipo de cliente
  Como clienta de la tienda
  Quiero que el envío sea gratis al superar el umbral, al ser cliente nueva,
  o al aplicar descuentos que igual dejen el monto sobre el umbral
  Para pagar el costo de envío correcto en cada pedido

  Esquema del escenario: El umbral de $50.000 se evalúa sobre el monto ya descontado, por región
    Dado un pedido sin cupones ni promociones, con un solo producto de $<monto> en la región "<region>"
    Y la clienta no es nueva
    Cuando calculo el resumen del pedido
    Entonces el envío cobrado es $<envio_esperado>

    Ejemplos:
      | monto | region        | envio_esperado |
      | 49999 | metropolitana | 3990           |
      | 50000 | metropolitana | 0              |
      | 49999 | extremo       | 12990          |
      | 50000 | extremo       | 0              |

  # 49999 y 12990 son los bordes: un peso bajo el umbral se cobra la tarifa de
  # la región (TRAMOS["extremo"] = 12990); en 50000 el envío ya es gratis,
  # sin importar la región.

  Escenario: Un cupón de monto fijo que baja el pedido bajo el umbral hace que el envío se cobre
    Dado un pedido con un solo producto de $52.000 en la región "metropolitana"
    Y la clienta no es nueva
    Y el pedido tiene un cupón de monto fijo por $3.000
    Cuando calculo el resumen del pedido
    Entonces el monto descontado es $49.000
    # 52.000 - 3.000 = 49.000
    Y el envío cobrado es $3.990
    # 49.000 < 50.000: aunque el subtotal ($52.000) superaba el umbral, el
    # cupón lo bajó antes de comparar. Confirma la decisión 1.

  Escenario: Una promoción que baja el pedido bajo el umbral hace que el envío se cobre
    Dado un pedido con un solo producto de $5.200 en cantidad 10 en la región "metropolitana"
    Y la clienta no es nueva
    Y el pedido tiene la promoción "volumen"
    Cuando calculo el resumen del pedido
    Entonces el monto descontado es $49.400
    # subtotal = 5.200 x 10 = 52.000
    # descuento por volumen (10+ unidades): 5% de 52.000 = 2.600
    # 52.000 - 2.600 = 49.400
    Y el envío cobrado es $3.990
    # 49.400 < 50.000: la promoción descuenta para el umbral igual que un
    # cupón. Confirma la decisión 3.

  Escenario: Una clienta nueva no paga envío aunque el pedido esté muy por debajo del umbral
    Dado un pedido con un solo producto de $10.000 en la región "metropolitana"
    Y la clienta es nueva
    Cuando calculo el resumen del pedido
    Entonces el envío cobrado es $0
    # cliente_nuevo=true tiene prioridad sobre el cálculo del umbral: se
    # ignora el monto por completo (envio.py revisa cliente_nuevo antes que
    # el umbral).

  Escenario: El IVA no cuenta para el umbral, aunque el monto con impuesto sí lo supere
    Dado un pedido sin cupones ni promociones, con un solo producto de $43.000 en la región "metropolitana"
    Y la clienta no es nueva
    Cuando calculo el resumen del pedido
    Entonces el IVA es $8.170
    # IVA = int(43.000 x 19 / 100) = int(8.170) = 8.170
    Y el monto con IVA incluido sería $51.170
    # 43.000 + 8.170 = 51.170 (esto por sí solo superaría el umbral)
    Pero el envío cobrado es $3.990
    # el umbral compara contra el monto descontado (43.000), sin IVA, que
    # sigue bajo $50.000. Confirma la decisión 2.
