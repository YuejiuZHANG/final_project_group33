from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import altair as alt
import pandas as pd
import json

app_ui = ui.page_fluid(
    ui.panel_title("Energy Efficiency by Community"),
    ui.input_select(id="community", label='Choose a Community',
                    choices=[]),
    output_widget('efficiency_trend'),
)


def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv("community_use.csv")

    @reactive.calc
    def subsetted_data():
        df = full_data()
        return df[df['community'] == input.community()]
    
    @render_altair
    def efficiency_trend():
        df = subsetted_data()

        chart = alt.Chart(df).mark_line(point = True).encode(
            alt.X("year:O"),
            alt.Y("ghg_efficiency:Q"),
            ).properties(width = 500, height = 300)
        
    @reactive.effect
    def update_dropdown():
        df = full_data()
        types_list = df['community'].unique().tolist()
        types_list = sorted(types_list)
        ui.update_select("community", choices=types_list)

app = App(app_ui, server)
