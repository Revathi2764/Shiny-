from shiny import App, ui, render, reactive
import pandas as pd
import faicons as fa
import calendar
import numpy as np
import seaborn as sns
import plotly.express as px
from shinywidgets import output_widget, render_widget
import matplotlib.pyplot as plt

# ICONS for value boxes
ICONS = {
    "sales": fa.icon_svg("chart-line"),
    "orders": fa.icon_svg("wallet"),
    "avg": fa.icon_svg("calculator"),
    "info": fa.icon_svg("circle-info")
}

# Define UI
app_ui = ui.page_fluid(
    # Header
    ui.div(
        ui.div(
            ui.div(
                fa.icon_svg("store", width="30px", height="30px", fill="white"),
                ui.h4("Sales Dashboard", class_="ms-3 mb-0"),
                class_="d-flex align-items-center"
            ),
            class_="navbar bg-primary text-white p-2"
        )
    ),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.card(
                ui.card_header("Controls"),
                ui.h4("Navigation", class_="mb-3"),
                ui.input_radio_buttons(
                    "nav",
                    "",
                    {"sales_data": "Sales Data", "heatmaps": "Heatmaps"},
                    selected="sales_data"
                ),
                ui.h4("Filters", class_="mt-4"),
                ui.input_select(
                    id="city",
                    label="Select a City:",
                    choices=[
                        "Dallas (TX)", "Boston (MA)", "Los Angeles (CA)",
                        "San Francisco (CA)", "Seattle (WA)", "Atlanta (GA)",
                        "New York City (NY)", "Portland (OR)", "Austin (TX)",
                        "Portland (ME)"
                    ]
                )
            ),
            class_="bg-light"  # Moved class_ to end of arguments
        ),
        
        # Main content
        ui.panel_conditional(
            "input.nav === 'sales_data'",
            ui.row(
                ui.column(4, ui.output_ui("sales_box")),
                ui.column(4, ui.output_ui("orders_box")),
                ui.column(4, ui.output_ui("avg_box"))
            ),
            ui.card(
                ui.card_header(
                    ui.div(
                        ui.h4("Sales Over Time", class_="d-inline me-2"),
                        ui.input_action_button(
                            "show_info",
                            "",
                            icon=fa.icon_svg("circle-info"),
                            class_="btn-link p-0"  # Moved class_ to end
                        ),
                        class_="d-flex align-items-center justify-content-between"
                    )
                ),
                ui.output_plot("sales_over_time_chart"),
                ui.modal(
                    "Analysis Summary",
                    ui.output_ui("sales_info_content"),
                    id="analysis_modal",
                    easy_close=True,
                    footer=None
                )
            ),
            ui.card(
                ui.output_data_frame("sales")
            )
        ),
        
        ui.panel_conditional(
            "input.nav === 'heatmaps'",
            ui.card(
                ui.card_header("Sales by Time of Day Heatmap"),
                ui.output_plot("plot_sales_by_time")
            ),
            ui.card(
                ui.card_header("Sales Distribution Map"),
                output_widget("sales_map")
            )
        )
    )
)

def server(input, output, session):
    @reactive.calc
    def dat():
        df = pd.read_csv("C:/Users/revat/Documents/datasets/sales.csv")
        df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
        df["month"] = df["order_date"].dt.month_name()
        df["hour"] = df["order_date"].dt.hour
        df["value"] = df["quantity_ordered"] * df["price_each"]
        return df

    @reactive.calc
    def metrics():
        df = dat()
        city_data = df[df['city'] == input.city()]
        
        total_sales = city_data["value"].sum()
        total_orders = city_data["quantity_ordered"].sum()
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        return total_sales, total_orders, avg_order_value

    @reactive.calc
    def sales_analysis():
        df = dat()
        city_data = df[df['city'] == input.city()]
        
        monthly_sales = city_data.groupby('month')['value'].sum()
        best_month = monthly_sales.idxmax()
        worst_month = monthly_sales.idxmin()
        
        total_sales = city_data['value'].sum()
        peak_hour = city_data.groupby('hour')['quantity_ordered'].sum().idxmax()
        
        return {
            'best_month': best_month,
            'worst_month': worst_month,
            'peak_hour': peak_hour,
            'total_sales': total_sales
        }

    @reactive.effect
    @reactive.event(input.show_info)
    def _():
        ui.modal_show("analysis_modal")

    @output
    @render.ui
    def sales_info_content():
        analysis = sales_analysis()
        return ui.div(
            ui.tags.p(
                ui.tags.strong("Best Performing Month: "), 
                analysis['best_month']
            ),
            ui.tags.p(
                ui.tags.strong("Lowest Performing Month: "), 
                analysis['worst_month']
            ),
            ui.tags.p(
                ui.tags.strong("Peak Sales Hour: "), 
                f"{analysis['peak_hour']}:00"
            ),
            class_="p-3"
        )

    @output
    @render.ui
    def sales_box():
        total_sales, _, _ = metrics()
        return ui.value_box(
            title=f"Total Sales in {input.city()}",
            value=f"${total_sales:,.0f}",
            showcase=ICONS["sales"],
            theme="bg-primary",
            height="150px"
        )

    @output
    @render.ui
    def orders_box():
        _, total_orders, _ = metrics()
        return ui.value_box(
            title=f"Total Orders in {input.city()}",
            value=f"{total_orders:,}",
            showcase=ICONS["orders"],
            theme="bg-success",
            height="150px"
        )

    @output
    @render.ui
    def avg_box():
        _, _, avg_order_value = metrics()
        return ui.value_box(
            title=f"Average Order Value in {input.city()}",
            value=f"${avg_order_value:,.2f}",
            showcase=ICONS["avg"],
            theme="bg-warning",
            height="150px"
        )

    @output
    @render.plot
    def sales_over_time_chart():
        df = dat()
        sales = df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
        sales_by_city = sales[sales["city"] == input.city()]
        
        month_map = {month: i for i, month in enumerate(calendar.month_name[1:], 1)}
        sales_by_city['month_num'] = sales_by_city['month'].map(month_map)
        sales_by_city = sales_by_city.sort_values('month_num')
        
        plt.figure(figsize=(12, 6))
        plt.bar(sales_by_city['month'], sales_by_city['quantity_ordered'])
        plt.title(f"Sales over Time -- {input.city()}")
        plt.xlabel("Month")
        plt.ylabel("Number of Orders")
        plt.xticks(rotation=45)
        plt.tight_layout()

    @output
    @render.data_frame
    def sales():
        df = dat()
        return df[df['city'] == input.city()].head(1000)

    @output
    @render.plot
    def plot_sales_by_time():
        df = dat()
        city_data = df[df['city'] == input.city()]
        sales_by_hour = city_data['hour'].value_counts().reindex(np.arange(0,24), fill_value=0)
        
        plt.figure(figsize=(10, 8))
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
        
        plt.title(f"Number of Orders by Hour of Day in {input.city()}")
        plt.xlabel("Hour of Day")
        plt.ylabel("Order Count")

    @output
    @render_widget
    def sales_map():
        df = dat()
        # Aggregate sales data by state
        df['state'] = df['city'].str.extract(r'\((.*?)\)').iloc[:, 0]
        state_sales = df.groupby('state')['value'].sum().reset_index()
        
        # Create choropleth map
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
        
        # Update layout
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

app = App(app_ui, server)