from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import altair as alt
import pandas as pd
import json 

app_ui = ui.page_fluid(
    ui.panel_title("Distribution of the Top 3 Least Efficient Building Types in 2022"),
    ui.input_select(id = 'efficiency_type', 
                    label = 'Select Efficiency Metric',
                    choices = ['Electricity','Gas','Greenhouse Gas'],
                    selected = 'Greenhouse Gas'),
    ui.input_checkbox("show", "Show Data"),
    ui.row(
        ui.column(8, 
            output_widget('chicago_map')),
        ui.column(4,  
            ui.panel_conditional(
                "input.show",
                ui.output_table("top10_table")))
    )
)


def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv("least_efficient.csv")
    
    @reactive.calc
    def subsetted_data():
        df = full_data()
        return df[df['type of efficiency'] == input.efficiency_type()]
    
    @render_altair
    def chicago_map():
        df = subsetted_data()
        top_3_list = df['property_type'].value_counts().head(3).index.tolist()
        filtered_data = df[df['property_type'].isin(top_3_list)]

        #Import Chicago Map
        file_path = "chicago-boundaries.geojson"
    
        with open(file_path) as f:
             chicago_geojson = json.load(f)
             
        geo_data = alt.Data(values=chicago_geojson["features"])

        #Create background
        background = alt.Chart(geo_data).mark_geoshape(
            fill='lightgrey',stroke='white'
            ).project(type = 'equirectangular'
                      ).properties(
                width = 700, height = 500)
        
        #Overlay with datapoints
        points = alt.Chart(filtered_data, title = "Map of Chicago").mark_circle(size=15).encode(
            longitude = 'lon_bin:Q',
            latitude = 'lat_bin:Q',
            color = alt.Color("property_type:N", 
                    sort = top_3_list,
                    legend = alt.Legend(title = "Property Type")),
            tooltip = ['property_type:N', 'community:N']).project(
                type = 'equirectangular').properties(
                    width = 700,height = 500)
        
        layered_chart = background + points

        return layered_chart
    
    @render.table
    def top10_table():
        df = subsetted_data()
        top10 = df['property_type'].value_counts().head(10).reset_index()
        top10 = top10.rename(columns = {
            'property_type':'Top 10 Property Types' ,
            'count':'Count (Out of 500 Least Efficient Buildings)'
        })

        return top10


app = App(app_ui, server)
