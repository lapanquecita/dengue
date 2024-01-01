"""

En los datasets de dengue, la columna de sexo tiene estos dos posibles valores:

MUJER: 1
HOMBRE: 2

"""

import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots

# Este diccionario es utilizado para convertir los
# identificadores de cada entidad a su nomre común.
ENTIDADES = {
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
}


def main(año):
    """
    Crea un mapa Choropleth y una tabla con la información
    detallada de casos confirmados de dengue en México.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Cargamos el dataset de población total por entidad.
    pop = pd.read_csv("./assets/poblacion_entidad/total.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    pop = pop[str(año)]

    # Renombramos algunos estados a sus nombres más comunes.
    pop = pop.rename(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz"
        }
    )

    # Cargamos el dataset de dengue del año que nos interesa.
    df = pd.read_csv(f"./data/{año}.csv")

    # IMPORTANTE: Solo seleccionamos casos confirmados.
    df = df[df["ESTATUS_CASO"] == 2]

    # Calculamos algunos totales para el subtítulo.
    total_nacional = len(df)
    poblacion_nacional = pop.iloc[0]
    tasa_nacional = total_nacional / poblacion_nacional * 100000

    subtitulo = f"Nacional: {tasa_nacional:,.2f} ({total_nacional:,.0f} registros)"

    # Quitamos los registros con entidades fuera de la reública mexicana.
    df = df[df["ENTIDAD_RES"] <= 32]

    # Transformamos el DataFrame para darnos el total de casos confirmados
    # por entidad y sexo.
    df = df.pivot_table(
        index="ENTIDAD_RES",
        columns="SEXO",
        aggfunc="count"
    ).fillna(0)["EDAD_ANOS"]

    # Renombramos el índice con los nombres de las entidades.
    df.index = df.index.map(ENTIDADES)

    # Creamos una nueva columna con el total por entidad.
    df["total"] = df.sum(axis=1)

    # Agregamos la columna de población con los datos del DataFrame de población total.
    df["poblacion"] = pop

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Ordenamos el DataFrame por la tasa de mayor a menor.
    df.sort_values("tasa", ascending=False, inplace=True)

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Para el valor máximo usamos el 95 percentil para mitigar los
    # efectos de valores atípicos.
    valor_min = df["tasa"].min()
    valor_max = df["tasa"].quantile(0.95)

    # Vamos a crear nuestra escala con 11 intervalos.
    marcas = np.linspace(valor_min, valor_max, 11)
    etiquetas = list()

    for marca in marcas:
        etiquetas.append(f"{marca:,.0f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el GeoJSON de México.
    geojson = json.load(open("./assets/mexico.json",  "r", encoding="utf-8"))

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones = list()
    valores = list()

    # Iteramos sobre las entidades dentro del GeoJSON.
    for item in geojson["features"]:

        # Extraemos el nombre de la entidad.
        geo = item["properties"]["NOM_ENT"]

        # Agregamos el objeto de la entidad y su valor a las listas correspondientes.
        ubicaciones.append(geo)
        valores.append(df.loc[geo, "tasa"])

    fig = go.Figure()

    # Configuramos nuestro mapa Choropleth con todas las variables antes definidas.
    # El parámetro 'featureidkey' debe coincidir con el de la variable 'geo' que
    # extrajimos en un paso anterior.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
            featureidkey="properties.NOM_ENT",
            colorscale="portland",
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickfont_size=20
            ),
            marker_line_color="#FFFFFF",
            marker_line_width=1.0,
            zmin=valor_min,
            zmax=valor_max
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor="#082032",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00"
    )

    # Seguimos personalizando varios parametros y
    # agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=False,
        font_family="Quicksand",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=40,
        margin_b=30,
        margin_l=40,
        width=1280,
        height=720,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.5,
                y=1.0,
                xanchor="center",
                yanchor="top",
                text=f"Distribución de casos confirmados de dengue en México durante el {año} por entidad de residencia",

                font_size=26
            ),
            dict(
                x=0.0275,
                y=0.45,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100k habitantes",
                font_size=16
            ),
            dict(
                x=0.5,
                y=-0.04,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
                font_size=22
            ),
            dict(
                x=0.01,
                y=-0.04,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA (13/12/{año})",
                font_size=22
            ),
            dict(
                x=1.01,
                y=-0.04,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
                font_size=22
            )
        ]
    )

    # Exportamos nuestro mapa a un archivo PNG.
    fig.write_image("./1.png")

    # Ahora sigue crear la tabla que irá debajo del mapa.
    # Creamos un lienzo con dos subplots de tipo Table.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[
            [
                {"type": "table"},
                {"type": "table"}
            ]
        ]
    )

    # Crear las tablas solo es cuestión de definir las columnas y sus
    # contenidos. Es importante notar en que columna y fila dentro de la
    # cuadrícula de subplots se coloca cada tabla.
    fig.add_trace(
        go.Table(
            columnwidth=[130, 70, 70, 70, 95],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total</b>",
                    "<b>100k habs. ↓</b>"
                ],
                font_color="#FFFFFF",
                fill_color="#f4511e",
                align="center",
                height=29.8,
                line_width=0.8),
            cells=dict(
                values=[
                    df.index[:16],
                    df[2][:16],
                    df[1][:16],
                    df["total"][:16],
                    df["tasa"][:16]
                ],
                fill_color="#041C32",
                height=29.8,
                format=["", ",", ",", ",", ",.2f"],
                line_width=0.8,
                align=["left", "center"]
            )
        ), col=1, row=1
    )

    fig.add_trace(
        go.Table(
            columnwidth=[130, 70, 70, 70, 95],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total</b>",
                    "<b>100k habs. ↓</b>"
                ],
                font_color="#FFFFFF",
                fill_color="#f4511e",
                align="center",
                height=29.8,
                line_width=0.8),
            cells=dict(
                values=[
                    df.index[16:],
                    df[2][16:],
                    df[1][16:],
                    df["total"][16:],
                    df["tasa"][16:]
                ],
                fill_color="#041C32",
                height=29.8,
                format=["", ",", ",", ",", ",.2f"],
                line_width=0.8,
                align=["left", "center"]
            )
        ), col=2, row=1
    )

    # Ajustamos el lienzo de las tablas.
    fig.update_layout(
        width=1280,
        height=560,
        font_family="Quicksand",
        font_color="white",
        font_size=17,
        margin_t=20,
        margin_r=40,
        margin_b=0,
        margin_l=40,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
    )

    # Exportamos las tablas a un archivo PNG.
    fig.write_image("./2.png")

    # Vamos a usar la librería Pillow para unir ambas imágenes.
    # Primero cargamos las dos imágenes recién creadas.
    imagen1 = Image.open("./1.png")
    imagen2 = Image.open("./2.png")

    # Calculamos el ancho y alto final de nuestra imagen.
    resultado_ancho = imagen1.width
    resultado_alto = imagen1.height + imagen2.height

    # Copiamos los pixeles de ambas imágenes.
    resultado = Image.new("RGB", (resultado_ancho, resultado_alto))
    resultado.paste(im=imagen1, box=(0, 0))
    resultado.paste(im=imagen2, box=(0, imagen1.height))

    # Exportamos la nueva imagen unida y borramos las originales.
    resultado.save(f"./estatal_{año}.png")

    os.remove("./1.png")
    os.remove("./2.png")


if __name__ == "__main__":

    main(2023)
