from shiny import App, render, ui
import matplotlib.pyplot as plt
import pandas as pd
import calendar

def load_data():
    df = pd.read_csv("C:/Users/revat/Documents/datasets/sales.csv")
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
    df["month"] = df["order_date"].dt.month_name()
    df["value"] = df["quantity_ordered"] * df["price_each"]
    return df

multiple_ui = ui.div(
    ui.navset_tab(
        ui.nav_panel("Page A",
            ui.layout_column_wrap(
                ui.navset_card_underline(
                    ui.nav_panel("Top Sellers",
                        ui.output_plot("plot_top_sellers")
                    ),
                    ui.nav_panel("Top Sellers Value ($)",
                        ui.output_plot("plot_top_sellers_value")
                    ),
                    ui.nav_panel("Lowest Sellers",
                        ui.output_plot("plot_lowest_sellers")
                    ),
                    ui.nav_panel("Lowest Sellers Value ($)",
                        ui.output_plot("plot_lowest_sellers_value")
                    ),
                    id="tab"
                ),
                width="50%"
            )
        ),
        ui.nav_panel("Page B",
            ui.card(
                ui.card_header("Page B Content"),
                ui.p("This is the content for page B"),
                ui.input_numeric("number_b", "Enter a number", 0),
                ui.output_text("output_b")
            )
        ),
        ui.nav_panel("Page C",
            ui.card(
                ui.card_header("Page C Content"),
                ui.p("This is the content for page C"),
                ui.input_slider("slider_c", "Select a value", 0, 100, 50),
                ui.output_text("output_c")
            )
        ),
        id="main_tabs"
    )
)

def multiple_server(input, output, session):
    @output
    @render.plot
    def plot_top_sellers():
        df = load_data()
        top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(top_sales['product'], top_sales['quantity_ordered'])
        ax.set_xlabel('Product')
        ax.set_ylabel('Quantity Ordered')
        ax.set_title(f'Top {input.n()} Products by Quantity Sold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def plot_top_sellers_value():
        df = load_data()
        top_sales = df.groupby('product')['value'].sum().nlargest(input.n()).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(top_sales['product'], top_sales['value'])
        ax.set_xlabel('Product')
        ax.set_ylabel('Total Sales Value ($)')
        ax.set_title(f'Top {input.n()} Products by Sales Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def plot_lowest_sellers():
        df = load_data()
        lowest_sales = df.groupby('product')['quantity_ordered'].sum().nsmallest(input.n()).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(lowest_sales['product'], lowest_sales['quantity_ordered'])
        ax.set_xlabel('Product')
        ax.set_ylabel('Quantity Ordered')
        ax.set_title(f'Bottom {input.n()} Products by Quantity Sold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def plot_lowest_sellers_value():
        df = load_data()
        lowest_sales = df.groupby('product')['value'].sum().nsmallest(input.n()).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(lowest_sales['product'], lowest_sales['value'])
        ax.set_xlabel('Product')
        ax.set_ylabel('Total Sales Value ($)')
        ax.set_title(f'Bottom {input.n()} Products by Sales Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig

    @output
    @render.text
    def output_b():
        return f"Square of your number: {input.number_b() ** 2}"
    
    @output
    @render.text
    def output_c():
        return f"Selected value: {input.slider_c()}"