"""

En los datasets de dengue, la columna de sexo tiene estos dos posibles valores:

MUJER: 1
HOMBRE: 2

"""

import pandas as pd
import plotly.graph_objects as go


# El dataset de dengue no cuenta con grupos de edad,
# nosotros tendremos que definirlos.
BINS = [
    (0, 4),
    (5, 9),
    (10, 14),
    (15, 19),
    (20, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 44),
    (45, 49),
    (50, 54),
    (55, 59),
    (60, 64),
    (65, 69),
    (70, 74),
    (75, 79),
    (80, 84),
    (85, 120),
]


def infecciones(año):
    """
    Crea una gráfica de dispersión donde se muestra el grupo de edad
    y sexo de las personas infectadas por dengue en México.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Cargamos el dataset de dengue del año que nos interesa.
    df = pd.read_csv(f"./data/{año}.csv")

    # IMPORTANTE: Solo seleccionamos casos confirmados.
    df = df[df["ESTATUS_CASO"] == 2]

    data = list()

    # Iteramos sobre todos nuestros grupos de edad y contamos los registros
    # para cada uno.
    for a, b in BINS:
        temp_mujeres = df[(df["SEXO"] == 1) & (df["EDAD_ANOS"].between(a, b))]
        temp_hombres = df[(df["SEXO"] == 2) & (df["EDAD_ANOS"].between(a, b))]

        # Para el último grupo de edad le agregamos el símbolo de 'mayor o igual que'
        # para que coincida con el índice de los datasets de población quinquenal.
        data.append(
            {
                "edad": f"{a}-{b}" if a < 85 else "≥85",
                "mujeres": len(temp_mujeres),
                "hombres": len(temp_hombres),
            }
        )

    # Creamos un DataFrame con los conteos de cada grupo de edad y sexo.
    final = pd.DataFrame.from_records(data, index="edad")

    # cargamos el dataset de la población de hombres por edad quinquenal.
    hombres_pop = pd.read_csv("./assets/poblacion_quinquenal/hombres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    hombres_pop = hombres_pop[str(año)]

    # Agregamos la columna de población de hombres.
    final["poblacion_hombres"] = hombres_pop

    # calculamos la tasa por cada 100k hombres para cada grupo de edad.
    final["tasa_hombres"] = final["hombres"] / final["poblacion_hombres"] * 100000

    # cargamos el dataset de la población de mujeres por edad quinquenal.
    mujeres_pop = pd.read_csv("./assets/poblacion_quinquenal/mujeres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    mujeres_pop = mujeres_pop[str(año)]

    # Agregamos la columna de población de mujeres.
    final["poblacion_mujeres"] = mujeres_pop

    # calculamos la tasa por cada 100k mujeres para cada grupo de edad.
    final["tasa_mujeres"] = final["mujeres"] / final["poblacion_mujeres"] * 100000

    # Vamos a crear dos gráficas de dispersión para comparar las tasas
    # de hombres y mujeres.
    fig = go.Figure()

    # Agregamos la gráfica de dispersión para hombres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_hombres"],
            mode="markers",
            name=f"<b>Hombres</b><br>{final['hombres'].sum():,.0f} registros",
            marker_color="#76ff03",
            marker_symbol="circle-open",
            marker_size=24,
            marker_line_width=4,
        )
    )

    # Agregamos la gráfica de dispersión para mujeres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_mujeres"],
            mode="markers",
            name=f"<b>Mujeres</b><br>{final['mujeres'].sum():,.0f} registros",
            marker_color="#ea80fc",
            marker_symbol="diamond-open",
            marker_size=24,
            marker_line_width=4,
        )
    )

    fig.update_xaxes(
        range=[-0.7, len(final) - 0.3],
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        title="Tasa por cada 100,000 hombres/mujeres dentro del grupo de edad",
        range=[-4, None],
        ticks="outside",
        separatethousands=True,
        title_font_size=18,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        mirror=True,
    )

    # Personalizamos la leyenda y agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.99,
        legend_y=0.98,
        legend_xanchor="right",
        legend_yanchor="top",
        legend_font_size=16,
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Incidencia de dengue en México durante el {año} según sexo y grupo de edad",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=85,
        margin_l=80,
        title_font_size=22,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: SSA (20/11/2024)",
            ),
            dict(
                x=0.5,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Grupo de edad al momento de la infección",
            ),
            dict(
                x=1.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./infecciones_edades_{año}.png")


def defunciones(año):
    """
    Crea una gráfica de dispersión donde se muestra el grupo de edad
    y sexo de las personas infectadas por dengue en México.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Cargamos el dataset de dengue del año que nos interesa.
    df = pd.read_csv(f"./data/{año}.csv")

    # IMPORTANTE: Solo seleccionamos defuncoines confirmadas.
    df = df[df["DICTAMEN"] == 1]

    data = list()

    # Iteramos sobre todos nuestros grupos de edad y contamos los registros
    # para cada uno.
    for a, b in BINS:
        temp_mujeres = df[(df["SEXO"] == 1) & (df["EDAD_ANOS"].between(a, b))]
        temp_hombres = df[(df["SEXO"] == 2) & (df["EDAD_ANOS"].between(a, b))]

        # Para el último grupo de edad le agregamos el símbolo de 'mayor o igual que'
        # para que coincida con el índice de los datasets de población quinquenal.
        data.append(
            {
                "edad": f"{a}-{b}" if a < 85 else "≥85",
                "mujeres": len(temp_mujeres),
                "hombres": len(temp_hombres),
            }
        )

    # Creamos un DataFrame con los conteos de cada grupo de edad y sexo.
    final = pd.DataFrame.from_records(data, index="edad")

    # cargamos el dataset de la población de hombres por edad quinquenal.
    hombres_pop = pd.read_csv("./assets/poblacion_quinquenal/hombres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    hombres_pop = hombres_pop[str(año)]

    # Agregamos la columna de población de hombres.
    final["poblacion_hombres"] = hombres_pop

    # calculamos la tasa por cada 100k hombres para cada grupo de edad.
    final["tasa_hombres"] = final["hombres"] / final["poblacion_hombres"] * 100000

    # cargamos el dataset de la población de mujeres por edad quinquenal.
    mujeres_pop = pd.read_csv("./assets/poblacion_quinquenal/mujeres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    mujeres_pop = mujeres_pop[str(año)]

    # Agregamos la columna de población de mujeres.
    final["poblacion_mujeres"] = mujeres_pop

    # calculamos la tasa por cada 100k mujeres para cada grupo de edad.
    final["tasa_mujeres"] = final["mujeres"] / final["poblacion_mujeres"] * 100000

    # Vamos a crear dos gráficas de dispersión para comparar las tasas
    # de hombres y mujeres.
    fig = go.Figure()

    # Agregamos la gráfica de dispersión para hombres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_hombres"],
            mode="markers",
            name=f"<b>Hombres</b><br>{final['hombres'].sum():,.0f} registros",
            marker_color="#76ff03",
            marker_symbol="circle-open",
            marker_size=24,
            marker_line_width=4,
        )
    )

    # Agregamos la gráfica de dispersión para mujeres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_mujeres"],
            mode="markers",
            name=f"<b>Mujeres</b><br>{final['mujeres'].sum():,.0f} registros",
            marker_color="#ea80fc",
            marker_symbol="diamond-open",
            marker_size=24,
            marker_line_width=4,
        )
    )

    fig.update_xaxes(
        range=[-0.7, len(final) - 0.3],
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        title="Tasa por cada 100,000 hombres/mujeres dentro del grupo de edad",
        range=[0, None],
        ticks="outside",
        separatethousands=True,
        titlefont_size=18,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        mirror=True,
    )

    # Personalizamos la leyenda y agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        legend_font_size=16,
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Defunciones por dengue en México durante el {año} según sexo y grupo de edad",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=85,
        margin_l=80,
        title_font_size=22,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: SSA (20/11/2024)",
            ),
            dict(
                x=0.5,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Grupo de edad al momento de la infección",
            ),
            dict(
                x=1.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./defunciones_edades_{año}.png")



if __name__ == "__main__":
    infecciones(2024)
    defunciones(2024)
