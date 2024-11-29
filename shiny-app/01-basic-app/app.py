from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import altair as alt
import pandas as pd
import json 

app_ui = ui.page_fluid(
    ui.panel_title("Efficiency by Property Type in 2022"),
    ui.input_select(id='property_type', 
                    label='Choose a Property Type',
                    choices=[], 
                    selected='Supermarket/Grocery Store'), 
    # ui.input_select(id='efficiency_type', 
    #                 label='Choose an Efficiency Type',
    #                 choices=['Electricity','Gas','Greenhouse Gas'],
    #                 selected='Electricity'),                
    output_widget('efficiency_trend')
)

def server(input, output, session):
    print("Server is running...")

    @reactive.calc
    def full_data():
        try:
            df = pd.read_csv("property_type_trend.csv")
            print(f"Data loaded successfully with {len(df)} rows and {len(df.columns)} columns.")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    @reactive.effect
    def update_dropdown():
        print("Updating dropdown with property types...")
        df = full_data()
        if df is not None:
            print(f"Full data has {len(df)} rows.")
            property_types = sorted(df['property_type'].unique())
            print(f"Available property types: {property_types}")

            default_selection = "Supermarket/Grocery Store" if "Supermarket/Grocery Store" in property_types else property_types[0]
            print(f"Setting default selection to: {default_selection}")

            ui.update_select("property_type", choices=property_types, selected=default_selection)
        else:
            print("No data loaded, skipping dropdown update.")

    @reactive.effect
    def log_selected_property_type():
        property_type = input.property_type()
        print(f"Property Type Selected: {property_type}")

    @reactive.calc
    def selected_property_type():
        prop_type = input.property_type()
        if prop_type is None or prop_type == "":
            print("Property type is None or empty, using default fallback.")
            df = full_data()
            if df is not None:
                prop_type = "Supermarket/Grocery Store" if "Supermarket/Grocery Store" in df['property_type'].unique() else "Unknown"
            else:
                prop_type = "Unknown"
        print(f"Reactive expression triggered for property type: {prop_type}")
        return prop_type

    @render_altair
    def emission_trend():
        df = full_data()
        if df is None:
            print("No data available for charting.")
            return alt.Chart()  # Return an empty chart temporarily
    
        print(f"Data loaded: {len(df)} rows")
        property_type = input.property_type()  # Use input from dropdown

        # Create and return the chart
        line_chart = alt.Chart(df).mark_line().encode(
            alt.X("year:O"),
            alt.Y("Greenhouse Gas:Q")
        ).properties( 
            width=500, 
            height=300
        )
        return line_chart



    # @reactive.calc
    # def subsetted_data_type():
    #     df = full_data()
    #     print(f"Original DataFrame shape: {df.shape}")  # Check before subsetting
    #     property_type = input.property_type()
    #     if property_type not in df['property_type'].unique():
    #         print(f"Property type '{property_type}' not found in the data.")
    #     return pd.DataFrame()  # If not found, return an empty DataFrame

    #     subsetted_df = df[df['property_type'] == property_type]
    #     print(f"Subsetted DataFrame shape: {subsetted_df.shape}")  # Check after subsetting
    #     return subsetted_df
    
    # @render_altair
    # def emission_trend():
        # #Reactive function for the property type
        # df = subsetted_data()
        # print("Subsetted DataFrame:\n", df.head())

        # #Account for the efficiency type
        # selected_emission = input.efficiency_type()
        # print("Selected Emission:", selected_emission)

        # if selected_emission not in df.columns:
        #     print(f"Error: {selected_emission} column not found in DataFrame.")
        #     return alt.Chart(pd.DataFrame()).mark_text().encode(text=alt.value("Invalid selection"))

        # chart_data = df.rename(columns={selected_emission: "value"})
        # print("Chart Data:\n", chart_data.head())

        # line_graph = alt.Chart(chart_data).mark_line(point = True).encode(
        #     alt.X("year:O"),
        #     alt.Y("value:Q")
        #     ).properties(
        #         title = f"Efficiency of {selected_emission} by {input.property_type()}",
        #         width = 500, 
        #         height = 300)
        # property_type = input.property_type()
        # print(f"Selected Property Type: {property_type}")
        
        # if property_type:
        #     print("Input exists and is valid")
        # else:
        #     print("No input value or input is None")
            
        # return alt.Chart()


    # @reactive.effect
    # def update_dropdown():
    #     df = full_data()
    #     types_list = df['property_type'].unique().tolist()
    #     types_list = sorted(types_list)
    #     ui.update_select('property_type', choices=types_list)


app = App(app_ui, server)
