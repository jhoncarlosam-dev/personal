# bandeja

Aplicación de consola en Python que ordena una carpeta de descargas y, si hay un CSV de gastos, resume los totales. Es una automatización empaquetada como programa: se configura con reglas, se puede simular y se puede volver a ejecutar.

El caso de uso es una bandeja donde llegan mezclados facturas, fotos, contratos y exportaciones de gastos. El mismo PDF a veces se descarga dos veces con otro nombre. `bandeja` clasifica cada archivo, aparta los duplicados por contenido y deja un reporte.

## Respuesta

Sí. He utilizado Python para automatizar un proceso repetitivo y para dejar esa automatización como una aplicación que se puede volver a ejecutar.

El caso es una carpeta de descargas donde se mezclan facturas, fotos, contratos, un CSV de gastos y, a veces, el mismo PDF guardado dos veces con otro nombre. A mano es fácil tratar esa copia como un archivo nuevo, o leer mal un monto colombiano: `25.000` son veinticinco mil y `1.200.000,50` usa punto de miles y coma decimal.

Para eso escribí `bandeja`, una aplicación de consola. El comando recorre la carpeta y clasifica cada archivo con reglas: si el nombre contiene `factura` o `recibo`, va a comprobantes; si no, decide la extensión. Compara el contenido con SHA-256. La copia va a `_duplicados` y el original se queda en la carpeta donde se archivó. Lo demás se mueve a `categoría/año/mes`, usando la fecha de modificación del archivo. Si un CSV trae fecha y monto, suma los gastos por categoría aunque el separador sea punto y coma. Con `--simular` imprime el plan, incluidos los totales, y deja la carpeta como estaba. Si una fila del CSV está dañada, la reporta y sigue con el resto.

En el ejemplo del proyecto, `factura-marzo.pdf` queda en `comprobantes/2026/03/`. El mismo archivo, renombrado `recibo-duplicado.pdf`, se reconoce como duplicado. `notas.txt` entra en `documentos/2026/04/` por su fecha de modificación. El CSV suma $1.228.500,50: alimentación 25.000, transporte 3.500 y hogar 1.200.000,50. Correrlo de nuevo deja el archivo como quedó.

## Requisitos

Python 3.11 o superior. La aplicación no instala dependencias para ejecutarse. Pytest se usa solo para las pruebas.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

```bash
bandeja ejemplo ejemplos/bandeja
bandeja ordenar ejemplos/bandeja --destino ejemplos/archivo --simular
bandeja ordenar ejemplos/bandeja --destino ejemplos/archivo --reporte ejemplos/reporte.md --json ejemplos/reporte.json
bandeja reglas > mis-reglas.toml
bandeja ordenar ./descargas --destino ./archivo --reglas mis-reglas.toml
```

`--reglas` reemplaza las reglas internas. Para partir de ellas, guarda la salida de `bandeja reglas` y edítala. `--sin-indice` no compara contra lo ya archivado; los duplicados de esa misma ejecución sí se detectan. `--recursivo` incluye subcarpetas.

La carpeta de destino no puede ser la bandeja ni estar una dentro de la otra.

## Ejemplo

`bandeja ejemplo` crea esta bandeja:

| Archivo | Qué demuestra |
| --- | --- |
| `factura-marzo.pdf` | el nombre manda: va a comprobantes |
| `recibo-duplicado.pdf` | el mismo contenido, con otro nombre |
| `recibo_dian.xml` | un recibo electrónico |
| `contrato.pdf` | un PDF que no es factura: va a documentos |
| `foto-viaje.png` | imagen |
| `notas.txt` | la fecha de modificación cae en abril |
| `gastos-marzo.csv` | gastos con `;` y montos colombianos |
| `archivo-raro.xyz` | sin regla: va a otros |
| `.borrador.txt` | oculto: se omite |
| `enlace-factura.pdf` | enlace simbólico: se omite y se reporta |

El CSV tiene una fila dañada (`no-es-un-monto`). Esa fila no entra al total y el archivo igual se archiva. El mes de la carpeta es la fecha de modificación del archivo; las fechas de cada fila solo se usan para validar el gasto.

Después de `bandeja ordenar`, el destino queda así:

```text
archivo/
├── _duplicados/recibo-duplicado.pdf
├── comprobantes/2026/03/factura-marzo.pdf
├── comprobantes/2026/03/recibo_dian.xml
├── documentos/2026/03/contrato.pdf
├── documentos/2026/04/notas.txt
├── hojas/2026/03/gastos-marzo.csv
├── imagenes/2026/03/foto-viaje.png
└── otros/2026/03/archivo-raro.xyz
```

El reporte muestra este total:

| Categoría | Total |
| --- | --- |
| Alimentación | 25.000,00 |
| Transporte | 3.500,00 |
| Hogar | 1.200.000,50 |
| **Total** | **1.228.500,50** |

## Comportamiento

- La primera regla con patrón que coincide gana. Después se usa la extensión.
- El nombre de la categoría es el nombre de la carpeta. Las categorías internas no llevan tilde; las del CSV conservan el texto de la fila.
- Dos archivos con el mismo contenido son un duplicado aunque el nombre cambie. Un CSV repetido no se suma dos veces.
- Si el nombre ya existe y el contenido es distinto, el nuevo se guarda con el sufijo `-2`. El archivo anterior permanece.
- Los archivos ocultos se omiten. Los enlaces simbólicos se omiten y aparecen en las advertencias.
- `--simular` no crea la carpeta de destino ni mueve archivos. Sí lee los CSV para calcular los totales.
- Si un movimiento falla a mitad de camino, lo ya movido queda aplicado y el comando termina con error. Se puede volver a ejecutar para el resto.
- La segunda ejecución no reubica lo que ya está en el destino.

## Reglas

```toml
[[regla]]
categoria = "comprobantes"
extensiones = ["pdf", "xml"]
patrones = ["factura", "recibo"]

[[regla]]
categoria = "imagenes"
extensiones = ["jpg", "png"]
```

Cada regla es una tabla `[[regla]]`. `patrones` se buscan dentro del nombre, sin importar mayúsculas, tildes, espacios o guiones bajos. Si la regla también lista extensiones, el patrón solo aplica a esas extensiones: `factura.pdf` es un comprobante y `foto.png` sigue siendo una imagen. La extensión es el sufijo final (`archivo.tar.gz` se lee como `gz`).

`bandeja reglas` imprime el conjunto interno: comprobantes, imagenes, documentos, hojas, audio, video, comprimidos y codigo.

## Gastos

Un CSV entra al resumen cuando el encabezado tiene una columna de fecha (`fecha`, `date` o `dia`) y una de monto (`monto`, `valor`, `importe`, `amount` o `total`). La categoría sale de `categoria`, `category` o `rubro`. Si no viene, se usa `concepto`, `descripcion`, `description` o `detalle`.

El separador se decide con la fila de encabezados. Así, un monto `1.200.000,50` en un CSV separado por `;` no se parte en dos columnas. Si el CSV usa coma, el monto con coma decimal va entre comillas.

| Texto | Valor |
| --- | --- |
| `25.000` | 25.000,00 |
| `3.500` | 3.500,00 |
| `1,50` y `1.50` | 1,50 |
| `1.200.000,50` | 1.200.000,50 |
| `1,234.56` | 1.234,56 |
| `(2.500)` | -2.500,00 |
| `1.000` | 1.000,00 |

Un grupo de exactamente tres dígitos es separador de miles, que es la lectura colombiana de `1.000`. Uno o dos dígitos son decimales. Si aparecen punto y coma, el último es el decimal. Una fila con fecha o monto ilegible se omite, se anota en el reporte y el resto se suma.

Fechas: `2026-03-15`, `15/03/2026` y `15-03-2026`. Cuando los dos primeros números pueden ser día o mes, se lee día/mes. `03/15/2026` se reconoce como 15 de marzo porque 15 no puede ser un mes.

## Pruebas

```bash
python -m pytest
```

Las pruebas cubren la clasificación, los montos colombianos, los duplicados, la simulación, el ejemplo completo y los comandos de consola.
