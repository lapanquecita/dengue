import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def mapa_municipios(año):
    """
    Crea un mapa Choropleth de casos confirmados
     de dengue en México por municipio.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Los identificadores los vamos a necesitar como cadenas.
    pop_types = {"clave_entidad": str, "clave_municipio": str}

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion2020.csv", dtype=pop_types)

    # El índice será lo que se conoce como el valor CVE.
    # Compuesto del identificador de entidad + el identificador de municipio.
    pop.index = pop["clave_entidad"] + pop["clave_municipio"]

    # Cargamos el dataset de dengue del año que nos interesa.
    df = pd.read_csv(f"./data/{año}.csv")

    # IMPORTANTE: Solo seleccionamos casos confirmados.
    df = df[df["ESTATUS_CASO"] == 2]

    # Arreglamos las columnas de los identificadores de entidad y municipio.
    df["ENTIDAD_RES"] = df["ENTIDAD_RES"].astype(str).str.zfill(2)
    df["MUNICIPIO_RES"] = df["MUNICIPIO_RES"].astype(str).str.zfill(3)

    # Calculamos el total de casos confirmados.
    total_casos = len(df)

    # Calculamos el total de población del año que nos interesa.
    total_pop = pd.read_csv(
        "./assets/poblacion_entidad/total.csv", index_col=0)
    total_pop = total_pop.loc["Estados Unidos Mexicanos", str(año)]

    # Arreglamos las columnas de los identificadores de entidad y municipio.
    df["ENTIDAD_RES"] = df["ENTIDAD_RES"].astype(str).str.zfill(2)
    df["MUNICIPIO_RES"] = df["MUNICIPIO_RES"].astype(str).str.zfill(3)

    # Creamos la columna CVE para el DataFrame de dengue.
    df["CVE"] = df["ENTIDAD_RES"] + df["MUNICIPIO_RES"]

    # Contamos el total de registro para cada CVE.
    df = df["CVE"].value_counts().to_frame("total")

    # Unimos ambos DataFrames.
    df = df.join(pop,)

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Para este mapa vamos a filtrar todos los municipios sin registros
    # ya que el dengue no afecta a todo el país y muchos valores en
    # cero puede sesgar los resultados.
    df = df[df["tasa"] != np.inf]
    df = df[df["tasa"] != 0]

    # Calculamos algunas estadísticas descriptivas.
    estadisticas = ["Estadísticas descriptivas"]
    estadisticas.append(f"Media: <b>{df['tasa'].mean():,.1f}</b>")
    estadisticas.append(f"Mediana: <b>{df['tasa'].median():,.1f}</b>")
    estadisticas.append(f"DE: <b>{df['tasa'].std():,.1f}</b>")
    estadisticas.append(f"25%: <b>{df['tasa'].quantile(.25):,.1f}</b>")
    estadisticas.append(f"75%: <b>{df['tasa'].quantile(.75):,.1f}</b>")
    estadisticas.append(f"95%: <b>{df['tasa'].quantile(.95):,.1f}</b>")
    estadisticas.append(f"Máximo: <b>{df['tasa'].max():,.1f}</b>")
    estadisticas = "<br>".join(estadisticas)

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Para el valor máximo usamos el 95 percentil para mitigar los
    # efectos de valores atípicos.
    valor_min = df["tasa"].min()
    valor_max = df["tasa"].quantile(0.95)

    # Vamos a crear nuestra escala con 13 intervalos.
    marcas = np.linspace(valor_min, valor_max, 13)
    etiquetas = list()

    for item in marcas:
        if item >= 10:
            etiquetas.append(f"{item:,.0f}")
        else:
            etiquetas.append(f"{item:,.1f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{valor_max:,.0f}"

    # Cargamos el GeoJSON de municipios de México.
    geojson = json.loads(open("./assets/mexico2020.json",
                              "r", encoding="utf-8").read())

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones = list()
    valores = list()

    # Iteramos sobre cada municipio e nuestro GeoJSON.
    for item in geojson["features"]:
        geo = str(item["properties"]["CVEGEO"])

        # Si el municipio no se encuentra en nuestro DataFrame,
        # agregamos un valor nulo.
        try:
            value = df.loc[geo]["total"]
        except:
            value = None

        # Agregamos el objeto del municipio y su valor a las listas correspondientes.
        ubicaciones.append(geo)
        valores.append(value)

    # Calculamos los valores para nuestro subtítulo.
    subtitulo = f"Nacional: {total_casos / total_pop * 100000:,.1f} ({total_casos:,.0f} casos confirmados)"

    fig = go.Figure()

    # Configuramos nuestro mapa Choropleth con todas las variables antes definidas.
    # El parámetro 'featureidkey' debe coincidir con el de la variable 'geo' que
    # extrajimos en un paso anterior.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
            featureidkey="properties.CVEGEO",
            colorscale="portland",
            marker_line_color="#FFFFFF",
            marker_line_width=1,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.035,
                y=0.5,
                thickness=150,
                ypad=400,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80
            ),

        )
    )

    # Vamos a sobreponer otro mapa Choropleth, el cual
    # tiene el único propósito de mostrar la división política
    # de las entidades federativas.

    # Cargamos el archivo GeoJSON de México.
    geojson_borde = json.loads(
        open("./assets/mexico.json", "r", encoding="utf-8").read())

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones_borde = list()
    valores_borde = list()

    # Iteramos sobre cada entidad dentro de nuestro archivo GeoJSON de México.
    for item in geojson_borde["features"]:

        geo = item["properties"]["NOM_ENT"]

        # Alimentamos las listas creadas anteriormente con la ubicación y su valor per capita.
        ubicaciones_borde.append(geo)
        valores_borde.append(1)

    # Este mapa tiene mucho menos personalización.
    # Lo único que necesitamos es que muestre los contornos
    # de cada entidad.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson_borde,
            locations=ubicaciones_borde,
            z=valores_borde,
            featureidkey="properties.NOM_ENT",
            colorscale=["hsla(0, 0, 0, 0)", "hsla(0, 0, 0, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=4.0,
            showscale=False,
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="locations",
        showocean=True,
        oceancolor="#04293A",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#000000"
    )

    # Agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=False,
        font_family="Quicksand",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=100,
        margin_b=30,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor="#064663",
        annotations=[
            dict(
                x=0.5,
                y=0.985,
                xanchor="center",
                yanchor="top",
                text=f"Distribución de los municipios con casos confirmados de dengue en México durante el {año}",
                font_size=140
            ),
            dict(
                x=0.02,
                y=0.49,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Casos confirmados por cada 100k habitantes",
                font_size=100
            ),
            dict(
                x=0.98,
                y=0.9,
                xanchor="right",
                yanchor="top",
                text=estadisticas,
                align="left",
                borderpad=30,
                bordercolor="#FFFFFF",
                bgcolor="#000000",
                borderwidth=5,
                font_size=120
            ),
            dict(
                x=0.01,
                y=-0.003,
                xanchor="left",
                yanchor="bottom",
                text="Fuente: SSA (13/12/2023)",
                font_size=120
            ),
            dict(
                x=0.5,
                y=-0.003,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
                font_size=120
            ),
            dict(
                x=1.0,
                y=-0.003,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=120
            ),
        ]
    )

    fig.write_image(f"./municipal_{año}.png")


def top_municipios_tabla(año):
    """
    Crea una tabla desglosando los 30 municipios con mayor incidencia
    de dengue en México.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Los identificadores los vamos a necesitar como cadenas.
    pop_types = {"clave_entidad": str, "clave_municipio": str}

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion2020.csv", dtype=pop_types)

    # El índice será lo que se conoce como el valor CVE.
    # Compuesto del identificador de entidad + el identificador de municipio.
    pop.index = pop["clave_entidad"] + pop["clave_municipio"]

    # Cargamos el dataset de dengue del año que nos interesa.
    df = pd.read_csv(f"./data/{año}.csv")

    # IMPORTANTE: Solo seleccionamos casos confirmados.
    df = df[df["ESTATUS_CASO"] == 2]

    # Arreglamos las columnas de los identificadores de entidad y municipio.
    df["ENTIDAD_RES"] = df["ENTIDAD_RES"].astype(str).str.zfill(2)
    df["MUNICIPIO_RES"] = df["MUNICIPIO_RES"].astype(str).str.zfill(3)

    # Creamos la columna CVE para el DataFrame de dengue.
    df["CVE"] = df["ENTIDAD_RES"] + df["MUNICIPIO_RES"]

    # Contamos el total de registro para cada CVE.
    df = df["CVE"].value_counts().to_frame("total")

    # Unimos ambos DataFrames.
    df = df.join(pop,)

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Creamos la columna de nombre que se compone del nombre de la entidad y municipio.
    df["nombre"] = df["municipio"] + ", " + df["entidad"]

    # Para esta tabla vamos a filtrar valores en 0
    # y solo tomaremos en cuenta municipios con al menos 100 casos confirmados.
    df = df[df["tasa"] != np.inf]
    df = df[df["tasa"] != 0]
    df = df[df["total"] >= 100]

    # Ordenamos los resultados por la tasa de mayor a menor.
    df.sort_values("tasa", ascending=False, inplace=True)

    # Reseteamos el índice y solo escogemos el top 30.
    df.reset_index(inplace=True)
    df.index += 1
    df = df.head(30)

    subtitulo = "Municipios con al menos 100 casos confirmados"

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[50, 200, 110, 80],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    f"<b>Municipio, Entidad</b>",
                    f"<b>Casos confirmados</b>",
                    "<b>100k habs. ↓</b>",
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#f4511e",
                align="center",
                height=28
            ),
            cells=dict(
                values=[
                    df.index,
                    df["nombre"],
                    df["total"],
                    df["tasa"]
                ],
                line_width=0.75,
                fill_color="#041C32",
                height=28,
                format=["", "", ",.0f", ",.2f"],
                align=["center", "left", "center"]
            )
        )
    )

    fig.update_layout(
        showlegend=False,
        width=840,
        height=1050,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=16,
        margin_t=110,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=26,
        title_text=f"Los 30 municipios de México con mayor incidencia de dengue<br>por cada 100k habitantes durante el {año}",
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA (13/12/{año})"
            ),
            dict(
                x=0.54,
                y=0.015,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=0.015,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./tabla_tasa.png")


if __name__ == "__main__":

    mapa_municipios(2023)
    top_municipios_tabla(2023)
