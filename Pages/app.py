from shiny import App, ui
from sales_page import sales_ui, sales_server
from heatmap_page import heatmap_ui, heatmap_server
from multiple_page import multiple_ui, multiple_server
import faicons as fa

app_ui = ui.page_fillable(
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Pages", class_="p-2"),
            ui.input_radio_buttons(
                "nav",
                "",
                {
                    "sales_data": "Sales Data", 
                    "heatmaps": "Heatmaps",
                    "multiple": "Multiple Pages"
                },
                selected="sales_data"
            ),
            ui.panel_conditional(
                "input.nav === 'sales_data'",
                ui.card(
                    ui.card_header("Select City"),
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
                )
            ),
            ui.panel_conditional(
                "input.nav === 'heatmaps'",
                ui.card(
                    ui.card_header("Select City"),
                    ui.input_select(
                        id="city_heatmap",
                        label="Select a City:",
                        choices=[
                            "Dallas (TX)", "Boston (MA)", "Los Angeles (CA)",
                            "San Francisco (CA)", "Seattle (WA)", "Atlanta (GA)",
                            "New York City (NY)", "Portland (OR)", "Austin (TX)",
                            "Portland (ME)"
                        ]
                    )
                )
            ),
            ui.panel_conditional(
                "input.nav === 'multiple'",
                ui.card(
                    ui.card_header("Settings"),
                    ui.input_numeric("n", "Number of Items", 5, min=0, max=20)
                )
            ),
            bg="bg-primary-subtle"
        ),
        # Main content
        ui.div(
            ui.div(
                ui.div(
                    fa.icon_svg("cash-register", width="20px", height="30px", fill="black"),
                    ui.h4("Sales Dashboard", class_="ms-3 mb-0"),
                    class_="d-flex align-items-center"
                ),
                class_="navbar bg-primary-subtle text-black p-2"
            ),            
        ),
        ui.panel_conditional(
            "input.nav === 'sales_data'",
            sales_ui
        ),
        ui.panel_conditional(
            "input.nav === 'heatmaps'",
            heatmap_ui
        ),
        ui.panel_conditional(
            "input.nav === 'multiple'",
            multiple_ui
        )
    )
)

def server(input, output, session):
    sales_server(input, output, session)
    heatmap_server(input, output, session)
    multiple_server(input, output, session)

app = App(app_ui, server)




