🇬🇧 [Read in English](README.md)
# A/B testing de campañas de email: análisis frecuentista, bayesiano y por segmentos

Análisis de un experimento aleatorizado de email marketing (el *MineThatData E-Mail Analytics Challenge* de Kevin Hillstrom, 2008): validación del diseño, estimación del efecto de cada campaña con intervalos de confianza y corrección por comparaciones múltiples, enfoque bayesiano y exploración de si el efecto cambia según el tipo de cliente.

**Autor:** Carlos Adolfo Peralta · [LinkedIn](https://www.linkedin.com/in/carlosperalta1993/) · [GitHub](https://github.com/CarlosAdolfoPeralta)

## Resumen

- **El experimento:** 64.000 clientes que compraron en los últimos 12 meses, asignados al azar a recibir un email con productos para **hombres**, un email con productos para **mujeres**, o ningún email (**control**). Se midió durante dos semanas si visitaron el sitio, si compraron y cuánto gastaron.
- **El diseño es sólido:** los tres grupos tienen el tamaño esperado (un tercio cada uno, p = 0,90) y son comparables en todo lo medido antes del experimento (diferencia estandarizada máxima de 0,009), por lo que las diferencias posteriores se pueden atribuir al email.
- **Los dos emails funcionan, y el de hombres rinde más:** frente al control, el email para hombres sube la conversión de 0,57 % a 1,25 % (+0,68 pp) y el de mujeres a 0,88 % (+0,31 pp). El de hombres supera al de mujeres por 0,37 pp. Todas las diferencias siguen siendo significativas tras la corrección por comparaciones múltiples.
- **Ingreso incremental (bruto):** unos 770 dólares por cada 1.000 emails con el email para hombres y unos 424 con el de mujeres, frente al control.
- **El enfoque bayesiano coincide:** la probabilidad de que el email para hombres supere al de mujeres en conversión es mayor a 99,9 %, y las conclusiones no dependen del prior.
- **Hallazgo exploratorio:** el efecto sobre la visita cambia mucho según el historial de compras del cliente. El email para mujeres casi no aumenta la visita entre quienes solo compraron productos de hombres (+1,1 pp), mientras que entre quienes compraron productos de mujeres suma +7,4 pp.

## Datos

| | |
|---|---|
| Fuente | Blog MineThatData, de Kevin Hillstrom (2008) |
| Clientes | 64.000, asignados al azar: control 21.306, email para hombres 21.307, email para mujeres 21.387 |
| Variables previas | recencia, historial de gasto, compras de productos de hombres y de mujeres, zona, cliente nuevo, canal |
| Resultados | `visit` (visitó el sitio), `conversion` (compró) y `spend` (gasto), en las dos semanas siguientes |
| Particularidades | el 99,1 % de los clientes tiene gasto cero; entre los 578 que compraron, el gasto máximo es exactamente 499 dólares en los tres grupos |

## Metodología

1. **Validación del experimento** (`01_validacion_experimento`): calidad de los datos, consistencia entre las variables resultado, *sample ratio mismatch* y balance de las características previas (chi-cuadrado, ANOVA, Kruskal-Wallis y diferencias estandarizadas). Incluye el **plan de análisis**, fijado antes de mirar los resultados: conversión como métrica principal; visita y gasto como secundarias; corrección de Holm dentro de cada métrica.
2. **Análisis frecuentista** (`02_analisis_frecuentista`):
   - Conversión y visita: diferencia absoluta con intervalo de Newcombe, aumento relativo con intervalo en escala logarítmica y prueba z de dos proporciones.
   - Gasto por cliente: prueba t de Welch más bootstrap de 10.000 remuestreos, por los ceros y la cola larga. Incluye sensibilidad a los montos altos y una advertencia sobre por qué no se compara causalmente el gasto entre compradores.
   - Potencia: efecto mínimo detectable y tamaño de muestra necesario.
3. **Enfoque bayesiano y segmentos** (`03_bayesiano_segmentos`):
   - Posteriores beta para las tasas, probabilidad de superioridad, pérdida esperada, sensibilidad al prior y bootstrap bayesiano para el gasto.
   - Análisis exploratorio por seis variables de segmentación, con prueba Q de Cochran de heterogeneidad y corrección de Holm.

Las funciones estadísticas están en `src/ab.py` y se validaron contra scipy (por ejemplo, la prueba z coincide con el chi-cuadrado 2x2 y Holm reproduce un caso conocido).

## Resultados

### Efecto de cada email frente al control y entre sí

| Métrica | Control | Email hombres | Email mujeres | Hombres − control | Mujeres − control | Hombres − mujeres |
|---|---|---|---|---|---|---|
| Conversión | 0,57 % | 1,25 % | 0,88 % | +0,68 pp (0,50 a 0,86) | +0,31 pp (0,15 a 0,47) | +0,37 pp (0,17 a 0,57) |
| Visita | 10,6 % | 18,3 % | 15,1 % | +7,7 pp (7,0 a 8,3) | +4,5 pp (3,9 a 5,2) | +3,1 pp (2,4 a 3,8) |
| Gasto por cliente | 0,65 USD | 1,42 USD | 1,08 USD | +0,77 USD (0,48 a 1,06) | +0,42 USD (0,17 a 0,69) | +0,35 USD (0,03 a 0,66) |

Intervalos de confianza del 95 % entre paréntesis (bootstrap en el gasto). Con la corrección de Holm, todas las diferencias son significativas al 5 %; la menos contundente es la del gasto entre emails (p = 0,03).

- **Aumento relativo de la conversión:** +119 % con el email para hombres (IC 77 % a 171 %) y +54 % con el de mujeres (IC 23 % a 94 %).
- **Origen del mayor gasto:** el gasto medio entre quienes compraron es parecido en los tres grupos (114, 114 y 122 dólares), por lo que el mayor ingreso por cliente proviene sobre todo de que compra más gente, no de compras más grandes.
- **Robustez:** al limitar el gasto al percentil 90 de los compradores, los efectos se mantienen (+0,67, +0,39 y +0,28 USD). Aplicando Holm sobre las nueve comparaciones a la vez, todas siguen siendo significativas.
- **Potencia:** con 21.306 clientes por grupo, el efecto mínimo detectable en conversión es de 0,22 pp (un aumento relativo de 39 %); detectar un aumento de 10 % habría requerido unos 286.000 clientes por grupo.

### Enfoque bayesiano

- La probabilidad de superioridad es mayor a 99,9 % en las tres comparaciones de conversión, y la probabilidad de que la diferencia entre emails supere 0,22 pp es de 93 %.
- Elegir el email para hombres tiene una pérdida esperada de prácticamente 0 pp de conversión; elegir el de mujeres, de 0,37 pp.
- Con tres priors distintos (uniforme, Jeffreys e informativo), la diferencia entre emails va de 0,353 a 0,369 pp: los datos dominan.
- En el gasto, el bootstrap bayesiano da resultados casi idénticos al frecuentista (diferencias menores a 0,01 USD) y una probabilidad de 98,5 % de que el email para hombres supere al de mujeres.

### ¿Cambia el efecto según el tipo de cliente? (exploratorio)

- **Conversión:** ninguna de las 18 pruebas de heterogeneidad es significativa tras Holm (el menor p ajustado es 0,15). El email para hombres tiene efecto positivo en los 22 segmentos analizados. Esta prueba tiene poca potencia con eventos raros, por lo que no se puede concluir que el efecto sea homogéneo.
- **Visita, según afinidad:** sí hay variación fuerte (p ajustado ≤ 0,0001), y es el hallazgo más claro de esta parte:

| Afinidad del cliente | Visita sin email | Efecto email hombres | Efecto email mujeres |
|---|---|---|---|
| Compró ambos tipos de productos | 18,1 % | +13,4 pp | +7,1 pp |
| Solo productos de hombres | 10,0 % | +6,9 pp | +1,1 pp |
| Solo productos de mujeres | 9,6 % | +7,1 pp | +7,4 pp |

  El email para mujeres rinde mucho menos fuera de su público natural. Es una hipótesis para un experimento nuevo (por ejemplo, no enviarlo a quienes solo compraron productos de hombres), no una conclusión definitiva: la visita es un paso intermedio y en conversión el patrón apunta en la misma dirección pero no es significativo.

## Limitaciones

- El ingreso es **bruto**: no se descuentan el costo de los emails ni el margen de los productos, que el dataset no trae.
- El seguimiento cubre solo dos semanas, y la muestra son clientes que compraron en los últimos 12 meses, por lo que los resultados no se extienden a clientes nuevos o inactivos.
- Los dos emails difieren en el contenido y en la audiencia a la vez, por lo que no se puede separar el efecto de uno y otro.
- El dataset no trae identificador de cliente, así que no se pudieron verificar duplicados. Que el gasto máximo sea exactamente 499 dólares en todos los grupos sugiere un tope en el registro (no verificado), aunque los resultados no dependen de los montos altos.
- La conversión es un evento raro (0,9 %): los intervalos del aumento relativo son amplios y el análisis por segmentos tiene poca potencia. Los segmentos son exploratorios y algunos tienen muy pocas compras.
- Para decidir a qué clientes enviar cada email se necesitaría un modelo de uplift, que excede este análisis.

## Estructura del repositorio

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── 01_validacion_experimento.ipynb
│   ├── 02_analisis_frecuentista.ipynb
│   └── 03_bayesiano_segmentos.ipynb
├── src/
│   ├── __init__.py
│   ├── data.py          # carga del dataset y validación del esquema
│   └── ab.py            # funciones estadísticas (proporciones, Holm, bootstrap, potencia, heterogeneidad)
├── reports/             # tablas de resultados (.csv)
└── data/                # datos descargados (no se versionan)
```

## Cómo reproducirlo

1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar los notebooks en orden desde la carpeta `notebooks/`. La primera vez, `src/data.py` descarga el dataset desde el blog de MineThatData y lo guarda en `data/raw/hillstrom.csv`. Si la descarga falla, se puede guardar el CSV manualmente en esa ruta.
3. Los notebooks 02 y 03 guardan sus tablas de resultados en `reports/`.

Las semillas están fijadas (42), por lo que el bootstrap y las simulaciones bayesianas son reproducibles.

## Referencias

- Hillstrom, K. (2008). *The MineThatData E-Mail Analytics And Data Mining Challenge*. Blog MineThatData. Fuente del dataset; los datos no se incluyen en este repositorio.
- Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. *Statistics in Medicine*, 17(8), 873-890.
