from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import altair as alt
import pandas as pd

app_ui = ui.page_fluid(
    ui.panel_title("Energy Efficiency by Property Type"),
    ui.input_select(id='property', label='Choose a Property Type',
                    choices=[]),
    ui.input_select(id='efficiency_type', 
                    label='Choose an Efficiency Type',
                    choices=['Electricity','Gas','Greenhouse Gas'],
                    selected='Greenhouse Gas'),
    ui.input_checkbox("show", "Show Data"),
    ui.row(
        ui.column(6, 
            output_widget('efficiency_trend')),
        ui.column(6,  
            ui.panel_conditional(
                "input.show",
                ui.output_table("subsetted_data_table")))
    )
) 


def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv("property_type_trend.csv")

    @reactive.calc
    def subsetted_data():
        df = full_data()
        return df[df['property_type'] == input.property()]
    
    @render.table
    def subsetted_data_table():
        df = subsetted_data()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.reset_index(drop=True)

        selected_emission = input.efficiency_type()
        rename_map = {
            "year": "Year",
            "Greenhouse Gas": "GHG Efficiency (Metric Tons CO2e/1000 sq ft)",
            "Electricity": "Electricity Efficiency (kBtu/1000 sq ft)",
            "Gas": "Gas Usage (kBtu/1000 sq ft)"
        }

        columns_to_keep = ["year", selected_emission]

        df = df[columns_to_keep]
        df = df.rename(columns={
            "year": rename_map["year"],
            selected_emission: rename_map[selected_emission]
        })

        return df
    
    @render_altair
    def efficiency_trend():
        df = subsetted_data()
        selected_emission = input.efficiency_type()

        chart_data = df.rename(columns={selected_emission: "value"})

        chart = alt.Chart(chart_data).mark_line(point = True).encode(
            alt.X("year:O").axis(title="Year"),
            alt.Y("value:Q").axis(title=f"{selected_emission}")
            ).properties(width = 500, height = 300)
        
        return chart
        
    @reactive.effect
    def _():
        df = full_data()
        types_list = df['property_type'].unique().tolist()
        types_list = sorted(types_list)
        ui.update_select('property', choices=types_list)


app = App(app_ui, server)
