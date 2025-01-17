# heatmap_page.py
from shiny import ui, render, reactive
import pandas as pd
import seaborn as sns
import plotly.express as px
from shinywidgets import output_widget, render_widget
import matplotlib.pyplot as plt

heatmap_ui = ui.div(
    ui.card(
        ui.card_header("Sales by Time of Day"),
        ui.output_plot("heatmap_time")
    ),
    ui.card(
        ui.card_header("Sales Distribution Map"),
        output_widget("sales_map")
    )
)

def heatmap_server(input, output, session):
    @reactive.calc
    def load_data():
        df = pd.read_csv("C:/Users/revat/Documents/datasets/sales.csv")
        df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
        df["hour"] = df["order_date"].dt.hour
        df["value"] = df["quantity_ordered"] * df["price_each"]
        return df

    @output
    @render.plot
    def heatmap_time():
        df = load_data()
        city_data = df[df['city'] == input.city_heatmap()]
        sales_by_hour = city_data['hour'].value_counts().reindex(range(24), fill_value=0)
        
        plt.figure(figsize=(12, 6))
        heatmap_data = sales_by_hour.values.reshape(24, 1)
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt="d",
            cmap="coolwarm",
            cbar=False,
            xticklabels=[],
            yticklabels=[f"{i}:00" for i in range(24)]
        )
        plt.title(f"Number of Orders by Hour of Day in {input.city_heatmap()}")
        plt.xlabel("Hour of Day")
        plt.ylabel("Order Count")
        plt.tight_layout()

    @output
    @render_widget
    def sales_map():
        df = load_data()
        df['state'] = df['city'].str.extract(r'\((.*?)\)').iloc[:, 0]
        state_sales = df.groupby('state')['value'].sum().reset_index()
        
        fig = px.choropleth(
            state_sales,
            locations='state',
            locationmode="USA-states",
            color='value',
            scope="usa",
            color_continuous_scale="Viridis",
            labels={'value': 'Total Sales ($)'},
            title='Sales Distribution by State'
        )
        
        fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            geo=dict(
                scope='usa',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                showframe=False,
                showcoastlines=True,
                projection_type='albers usa'
            )
        )
        return fig




