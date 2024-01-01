"""

Una gráfica de tipo calendario es esencialmente un mapa de calor (heatmap).
sin embargo, nuestra versión es más complicada al tener más detalles visuales.

"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots

# Estas abreviaciones son usadas para las etiquetas arriba del calenario.
MESES_ABREVIACIONES = [
    "Ene.", "Feb.", "Mar.", "Abr.",
    "May.", "Jun.", "Jul.", "Ago.",
    "Sep.", "Oct.", "Nov.", "Dic."
]

# Estos nombres son utilizados para la tabla de estadísticas.
MESES_NOMBRES = [
    "enero", "febrero", "marzo", "abril",
    "mayo", "junio", "julio", "agosto",
    "septiembre", "octubre", "noviembre", "diciembre"
]

# Estas llaves y valores son utilizados para el eje vertical del calendario.
DIAS_DICT = {
    0: "Lun.",
    1: "Mar.",
    2: "Mié.",
    3: "Jue.",
    4: "Vie.",
    5: "Sáb.",
    6: "Dom."
}


def main(año):
    """
    Crea un calendario donde se muestra el número de nuevas
    infecciones por día de dengue en México.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Cargamos el dataset de dengue del año que nos interesa.
    # Seleccinamos la columna de 'FECHA_SIGN_SINTOMAS' como nuestro índice.
    df = pd.read_csv(
        f"./data/{año}.csv",
        parse_dates=["FECHA_SIGN_SINTOMAS"],
        index_col="FECHA_SIGN_SINTOMAS",
        dayfirst=True,
    )

    # IMPORTANTE: Solo seleccionamos casos confirmados.
    df = df[df["ESTATUS_CASO"] == 2]

    # Contamos que mes tuvo más registros.
    mes_max = df.index.month.value_counts()[:1]

    # Contamos los totales por día.
    # El método 'resample' es bastante útil al tener un índice tipo DateTimeIndex.
    totales_por_dia = df.resample("D").count()["ESTATUS_CASO"]

    # Creamos el cascarón de un DataFrame para todos los días del año de interés.
    # Después le asignamos los valores de los totales recién calculados.
    final = pd.DataFrame(
        index=pd.date_range(f"{año}-01-01", f"{año}-12-31"),
        data={"total": totales_por_dia}
    )

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Para el valor máximo usamos el 95 percentil para mitigar los
    # efectos de valores atípicos.
    valor_min = final["total"].min()
    valor_max = final["total"].quantile(0.95)

    # Vamos a crear nuestra escala con 9 intervalos.
    marcas = np.linspace(valor_min, valor_max, 9)
    etiquetas = list()

    for marca in marcas:
        etiquetas.append(f"{marca:,.0f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    #################################################
    # A partir de aquí las cosas se ponen complicadas.
    #################################################

    # Un año tiene por lo general de 52 a 53 semanas
    # pero cada 28 años tiene 54.

    # Parte del algoritmo es asignarle un número de semana a cada día.
    # No podemos usar la propiedad 'week' del objeto DateTime ya que nos
    # devuelve la del calendario Gregoriano (que puede ser del año anterior).

    # Vamos a crear una lista que nos da 7 veces el número de semana
    # para 54 semanas.
    numero_semana = list()

    for semana in range(54):
        numero_semana.extend([semana for _ in range(7)])

    # Creamos una columna con el día de la semana.
    # Donde 0 es lunes y 6 es domingo.
    final["dayofweek"] = final.index.dayofweek

    # Para determinar el número de semana de tada día
    # debemos ajustar desde el primer día del año (semana 0).
    # Pero no todos los años comienzan en lunes.
    # Lo que hacemos es recortar nuestra lista de numero de semana
    # exactamente donde comienza el año y donde termina y el
    # resultado se agrega a una nueva columna en el DataFrame.
    pad = final.index[0].dayofweek
    final["semana"] = numero_semana[pad:len(final) + pad]

    # En nuestro calendario, el primer día de cada mes tendrá un borde para distinguirlo.
    final["borde"] = final.index.map(lambda x: 1 if x.day == 1 else 0)

    # Calculamos algunas estadísticas que irán debajo del calendario.
    stats_max = f"{final['total'].max():,.0f} el {final['total'].idxmax():%d/%m/%Y}"
    month_max = f"{mes_max.max():,.0f} en {MESES_NOMBRES[mes_max.idxmax() - 1]}"
    stats_total = f"{final['total'].sum():,.0f}"
    stats_mean = f"{final['total'].sum() / len(final):,.1f}"

    # Las etiquetas de los meses estarán uniformemente espaciados.
    marcas_meses = np.linspace(1.5, 49.5, 12)

    # Vamos a crear un lienzo con tres elmentos:
    # (2) Heatmaps sobrepuestos y (1) Table
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[250, 150],
        vertical_spacing=0.07,
        specs=[
            [{"type": "scatter"}],
            [{"type": "table"}]
        ]
    )

    # El primer Heatmap va a tener un solo proposito y es el
    # de mostrar el borde en el primer día de cada mes.
    # Es importante poner atención en los parámetros 'gap', ya que
    # el borde es un truco visual.
    fig.add_trace(
        go.Heatmap(
            x=final["semana"],
            y=final["dayofweek"],
            z=final["borde"],
            xgap=1,
            ygap=12,
            colorscale=["hsla(0, 100%, 100%, 0.0)",
                        "hsla(0, 100%, 100%, 1.0)"],
            showscale=False,
        ), col=1, row=1
    )

    # Este heatmap va a mostrar los valores de cada día.
    # Está configurado con la mayoría de variables que definimos anteriormente.
    fig.add_trace(
        go.Heatmap(
            x=final["semana"],
            y=final["dayofweek"],
            z=final["total"],
            xgap=5,
            ygap=16,
            zmin=valor_min,
            zmax=valor_max,
            colorscale="rainbow",
            colorbar=dict(
                title_text="<br>Número de registros",
                title_side="right",
                y=0.6,
                ticks="outside",
                outlinewidth=1.5,
                thickness=20,
                outlinecolor="#FFFFFF",
                tickwidth=2,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickfont_size=16,
                tickvals=marcas,
                ticktext=etiquetas,
            )
        ), col=1, row=1
    )

    # Agregamos una sencilla tabla con las estadísticas que calculamos anteriormente.
    fig.add_trace(
        go.Table(
            header=dict(
                values=[
                    "<b>Día con más registros</b>",
                    "<b>Mes con más registros</b>",
                    "<b>Total anual</b>",
                    "<b>Promedio diario</b>"
                ],
                font_color="#FFFFFF",
                fill_color="#f4511e",
                align="center",
                height=32,
                line_width=0.8),
            cells=dict(
                values=[
                    stats_max,
                    month_max,
                    stats_total,
                    stats_mean,
                ],
                fill_color="#041C32",
                height=32,
                line_width=0.8,
                align="center"
            )
        ), col=1, row=2
    )

    # Es importante fijar el rango del eje horizontal para
    # evitar que se distorcione.
    fig.update_xaxes(
        range=[-1, final["semana"].max() + 1],
        side="top",
        tickfont_size=20,
        ticktext=MESES_ABREVIACIONES,
        tickvals=marcas_meses,
        ticks="outside",
        ticklen=5,
        tickwidth=0,
        linecolor="#FFFFFF",
        tickcolor="#041C32",
        showline=True,
        zeroline=False,
        showgrid=False,
        mirror=True,
    )

    # Al igual que con el eje horizontal, fijamos el rango para darle
    # suficiente espacio a cada día de la semana.
    fig.update_yaxes(
        range=[6.75, -0.75],
        ticktext=list(DIAS_DICT.values()),
        tickvals=list(DIAS_DICT.keys()),
        ticks="outside",
        tickfont_size=16,
        ticklen=10,
        title_standoff=0,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        zeroline=False,
        showgrid=False,
        mirror=True,
    )

    # Un poco más de personalización y agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=False,
        width=1280,
        height=533,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=20,
        title_text=f"Día de inicio de síntomas de infecciones por dengue en México durante el {año}",
        title_x=0.5,
        title_y=0.93,
        margin_t=120,
        margin_r=140,
        margin_b=0,
        margin_l=90,
        title_font_size=30,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.01,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA (13/12/{año})"
            ),
            dict(
                x=0.5,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="El □ Indica el inicio de cada mes"
            ),
            dict(
                x=1.01,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image(f"./calendario_{año}.png")


if __name__ == "__main__":

    main(2023)
