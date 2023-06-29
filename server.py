import pandas as pd
from dash import Dash, Input, Output, html, dcc
import plotly.graph_objects as go
import plotly.express as px

# Load data
data = pd.read_csv("data/bulldozer.csv")
data["saledate"] = pd.to_datetime(data["saledate"], format="%m/%d/%Y %H:%M")

# Load external styling
external_stylesheets = [
    "https://fonts.cdnfonts.com/css/museo",
]

# Set up app
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Bulldozer Analytics"

# Set up layout
app.layout = html.Div(
    children=[
        # Header
        html.Div(
            children=[
                html.P(
                    children="🚜",
                    style={
                        "fontSize": "48px",
                        "margin": "0 auto",
                        "textAlign": "center",
                    },
                ),
                html.H1(children="Bulldozer Analytics", className="header-title"),
                html.P(
                    children="Analyze the monthly bulldozer auction sales!",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        # Menu
        html.Div(
            children=[
                html.Div(
                    [
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": prod_type, "value": prod_type}
                                for prod_type in data["ProductGroupDesc"].unique()
                            ],
                            clearable=True,
                            searchable=False,
                            placeholder="Filter on machine type...",
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(children="Region", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in data["state"].unique()
                            ],
                            clearable=True,
                            searchable=False,
                            placeholder="Filter on region...",
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(children="Aggregation", className="menu-title"),
                        dcc.Dropdown(
                            id="agg-filter",
                            options=["Daily", "Monthly", "Yearly"],
                            value="Daily",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        # Graph and info box
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="sales-fig",
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


# Set up callbacks
@app.callback(
    Output("sales-fig", "figure"),
    Input("type-filter", "value"),
    Input("region-filter", "value"),
    Input("agg-filter", "value"),
)
def update_figure(
    machine_type: str | None, region: str | None, agg_period: str
) -> go.Figure:
    """
    Updates the sales figure based on the input data.
    """
    plot_data = data.copy()

    if machine_type:
        plot_data = plot_data[plot_data["ProductGroupDesc"] == machine_type]
    if region:
        plot_data = plot_data[plot_data["state"] == region]

    plot_data = plot_data[["saledate", "SalePrice"]]

    if agg_period == "Daily":
        date_format = "|%Y-%m-%d"
    if agg_period == "Monthly":
        date_format = "|%Y-%m"
        plot_data = plot_data.resample("m", on="saledate").sum()
    elif agg_period == "Yearly":
        date_format = "|%Y"
        plot_data = plot_data.resample("Y", on="saledate").sum()

    fig = px.line(
        data_frame=plot_data.groupby("saledate").sum().reset_index(),
        x="saledate",
        y="SalePrice",
        hover_data={
            "saledate": date_format,
            "SalePrice": ":$,.2f",
        },
        labels={"saledate": "Sale date", "SalePrice": "Total sale price"},
        color_discrete_sequence=["#079a82"]
    )
    fig.update_layout(hovermode="x unified")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
