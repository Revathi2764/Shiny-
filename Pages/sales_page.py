# sales_page.py
from shiny import ui, render, reactive
import pandas as pd
import faicons as fa
import calendar
import matplotlib.pyplot as plt

# ICONS for value boxes
ICONS = {
    "sales": fa.icon_svg("chart-line"),
    "orders": fa.icon_svg("wallet"),
    "avg": fa.icon_svg("calculator")
}

sales_ui = ui.div(
    ui.row(
        ui.column(4, ui.output_ui("sales_box")),
        ui.column(4, ui.output_ui("orders_box")),
        ui.column(4, ui.output_ui("avg_box"))
    ),
    ui.card(
        ui.card_header("Sales Over Time"),
        ui.output_plot("sales_over_time_chart")
    ),
    ui.card(
        ui.card_header("Sales Data"),
        ui.output_data_frame("sales_table")
    )
)

def sales_server(input, output, session):
    @reactive.calc
    def load_data():
        df = pd.read_csv("C:/Users/revat/Documents/datasets/sales.csv")
        df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
        df["month"] = df["order_date"].dt.month_name()
        df["value"] = df["quantity_ordered"] * df["price_each"]
        return df

    @reactive.calc
    def city_metrics():
        df = load_data()
        city_data = df[df['city'] == input.city()]
        
        total_sales = city_data["value"].sum()
        total_orders = city_data["quantity_ordered"].sum()
        avg_order = total_sales / total_orders if total_orders > 0 else 0
        
        return total_sales, total_orders, avg_order

    @output
    @render.ui
    def sales_box():
        total_sales, _, _ = city_metrics()
        return ui.value_box(
            "Total Sales",
            f"${total_sales:,.2f}",
            showcase=ICONS["sales"],
            theme="bg-danger-subtle"
        )

    @output
    @render.ui
    def orders_box():
        _, total_orders, _ = city_metrics()
        return ui.value_box(
            "Total Orders",
            f"{total_orders:,}",
            showcase=ICONS["orders"],
            theme="bg-light"
        )

    @output
    @render.ui
    def avg_box():
        _, _, avg_order = city_metrics()
        return ui.value_box(
            "Average Order Value",
            f"${avg_order:,.2f}",
            showcase=ICONS["avg"],
            theme="bg-warning-subtle"
        )

    @output
    @render.plot
    def sales_over_time_chart():
        df = load_data()
        city_data = df[df['city'] == input.city()]
        
        monthly_sales = city_data.groupby('month')['quantity_ordered'].sum().reset_index()
        month_order = {month: idx for idx, month in enumerate(calendar.month_name[1:])}
        monthly_sales['month_num'] = monthly_sales['month'].map(month_order)
        monthly_sales = monthly_sales.sort_values('month_num')
        
        plt.figure(figsize=(12, 6))
        plt.bar(monthly_sales['month'], monthly_sales['quantity_ordered'])
        plt.title(f"Sales over Time -- {input.city()}")
        plt.xlabel("Month")
        plt.ylabel("Number of Orders")
        plt.xticks(rotation=45)
        plt.tight_layout()

    @output
    @render.data_frame
    def sales_table():
        df = load_data()
        return df[df['city'] == input.city()].head(1000)





