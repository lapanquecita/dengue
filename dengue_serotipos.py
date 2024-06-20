import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
from plotly.subplots import make_subplots


SEROTIPOS = {
    1: "DENV-1",
    2: "DENV-2",
    3: "DENV-3",
    4: "DENV-4",
    5: "Sin serotipo aislado",
}


def main(año):
    """
    Crea gráficas de dona con los casos confirmados y
    defunciones por dengue desagregadas por serotipo.

    Parameters
    ----------
    año: int
        El año que se desea graficar.

    """

    # Cargamos el dataset de dengue del año que nos interesa.
    df = pd.read_csv(f"./data/{año}.csv")

    # Seleccionamos los casos confirmados y agrupamos por serotipo.
    casos = (
        df[df["ESTATUS_CASO"] == 2]["RESULTADO_PCR"]
        .value_counts()
        .to_frame("total")
        .sort_index()
    )
    casos.index = casos.index.map(SEROTIPOS)
    casos["perc"] = casos["total"] / casos["total"].sum() * 100

    casos["texto"] = casos.apply(
        lambda x: f"<b>{x['perc']:,.2f}%</b><br>({x['total']:,.0f})", axis=1
    )

    # Seleccionamos las defunciones y agrupamos por serotipo.
    defunciones = (
        df[df["DICTAMEN"] == 1]["RESULTADO_PCR"]
        .value_counts()
        .to_frame("total")
        .sort_index()
    )
    defunciones.index = defunciones.index.map(SEROTIPOS)
    defunciones["perc"] = defunciones["total"] / defunciones["total"].sum() * 100

    defunciones["texto"] = defunciones.apply(
        lambda x: f"<b>{x['perc']:,.2f}%</b><br>({x['total']:,.0f})", axis=1
    )

    # Definimos los títulos para cada gráfica de dona.
    titulos = [
        f"<b>{casos['total'].sum():,}</b><br>Casos",
        f"<b>{defunciones['total'].sum():,}</b><br>Defs.",
    ]

    # Crearemos dos gráficas de dona, una para casos confirmados y una para defunciones.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.12,
        subplot_titles=titulos,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
    )

    fig.add_trace(
        go.Pie(
            labels=casos.index,
            values=casos["total"],
            text=casos["texto"],
            texttemplate="%{text}",
            hole=0.75,
            textposition="outside",
            marker_line_color="#041C32",
            marker_line_width=5,
            sort=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Pie(
            labels=defunciones.index,
            values=defunciones["total"],
            text=defunciones["texto"],
            texttemplate="%{text}",
            hole=0.75,
            textposition="outside",
            marker_line_color="#041C32",
            marker_line_width=5,
            sort=False,
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        colorway=qualitative.Vivid,
        legend_orientation="h",
        showlegend=True,
        legend_itemsizing="constant",
        legend_x=0.5,
        legend_y=-0.15,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Casos confirmados y defunciones por dengue en México durante el {año} por serotipo",
        title_x=0.5,
        title_y=0.95,
        margin_t=130,
        margin_l=40,
        margin_r=40,
        margin_b=120,
        title_font_size=26,
        paper_bgcolor="#041C32",
    )

    # Ajustamos la posición y el tamaño de los títulos de cada gráfica.
    for annotation in fig["layout"]["annotations"]:
        annotation["y"] = 0.5
        annotation["yanchor"] = "middle"
        annotation["font"]["size"] = 70

    fig.add_annotation(
        x=-0.05,
        xanchor="left",
        xref="paper",
        y=-0.28,
        yanchor="bottom",
        yref="paper",
        text="Fuente: SSA (03/01/2024)",
    )

    fig.add_annotation(
        x=1.05,
        xanchor="right",
        xref="paper",
        y=-0.28,
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapanquecita",
    )

    fig.write_image(f"./serotipos_{año}.png")


if __name__ == "__main__":
    main(2023)
