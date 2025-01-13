from shiny import reactive
from shiny.express import input, ui, render, app
import pandas as pd
import faicons as fa
import altair as alt
import calendar
import numpy as np
import seaborn as sns
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
from shinywidgets import render_widget

# ICONS for value boxes
ICONS = {
    "sales": fa.icon_svg("chart-line"),
    "orders": fa.icon_svg("wallet"),
    "avg": fa.icon_svg("calculator"),
}

# Define a function to load and preprocess the data
@reactive.calc
def dat():
    df = pd.read_csv("C:/Users/revat/Documents/datasets/sales.csv") 
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
    df["month"] = df["order_date"].dt.month_name()
    df["hour"] = df["order_date"].dt.hour
    df["value"] = df["quantity_ordered"] * df["price_each"]
    return df

# Modified metrics calculation to filter by selected city
@reactive.calc
def metrics():
    df = dat()
    # Filter data for selected city
    city_data = df[df['city'] == input.city()]
    
    total_sales = city_data["value"].sum()
    total_orders = city_data["quantity_ordered"].sum()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    return total_sales, total_orders, avg_order_value

# Set page options
app.title = "Sales Dashboard"

# Create header
with ui.layout_columns(col_widths=[12], class_="navbar bg-primary text-white p-2"):
    with ui.layout_columns(col_widths=[1, 11], class_="d-flex align-items-center"):
        ui.div(fa.icon_svg("store", width="30px", height="30px", fill="white"))
        ui.h4("Sales Dashboard", class_="ms-3 mb-0")

# Create main content
with ui.navset_card_underline():
    with ui.nav_panel("Sales Data"):
        with ui.layout_sidebar():
            with ui.sidebar():
                "Sales Metrics"
                
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

            # Value boxes outside sidebar using layout_columns
            with ui.layout_columns(cols=3):
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

            # Charts
            with ui.card():
                @render_widget
                def sales_over_time_altair():
                    df = dat()
                    sales = df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
                    sales_by_city = sales[sales["city"] == input.city()]
                    month_orders = list(calendar.month_name)[1:]
                    
                    chart = alt.Chart(sales_by_city).mark_bar().encode(
                        x=alt.X('month', sort=month_orders),
                        y='quantity_ordered',
                        tooltip=['month', 'quantity_ordered']
                    ).properties(
                        title=f"Sales over Time -- {input.city()}"
                    )
                    return chart

            with ui.card():
                @render.data_frame
                def sales():
                    df = dat()
                    # Filter the dataframe by selected city
                    return df[df['city'] == input.city()].head(1000)

    with ui.nav_panel("Heatmaps"):
        with ui.layout_columns(cols=1):
            with ui.card():
                with ui.card_header():
                    "Sales by Time of Day Heatmap"

                @render.plot
                def plot_sales_by_time():
                    df = dat()
                    # Filter data for selected city
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

            with ui.card():
                with ui.card_header():
                    "Sales by Location Map"

                @render.ui
                def plot_us_heatmap():
                    df = dat()
                    # Filter data for selected city
                    city_data = df[df['city'] == input.city()]
                    heatmap_data = city_data[['lat', 'long', 'quantity_ordered']].values
                    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
                    HeatMap(heatmap_data).add_to(map)
                    return map
