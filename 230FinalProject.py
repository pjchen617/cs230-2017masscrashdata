"""
Name:       Patrick Chen
CS230:      Section 230-6
Data:       Massachusetts Car Crashes 2017
URL:        Link to your web application on Streamlit Cloud (if posted)

Description:

This Streamlit application visualizes car crash data from Massachusetts in 2017, allowing users to explore details through interactive maps and charts. Users can filter crashes by severity and location, and analyze crash causes in different cities and towns.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide")

# [PY3] A function that returns a value and is called in at least two different places in your program
def read_data():
    return pd.read_csv("2017_Crashes_10000_sample.csv")
df = read_data()

# Creating the scatterplot map with streamlit and pydeck (https://deckgl.readthedocs.io/en/latest/index.html - used to
# learn mapping functions)
# [VIZ4] At least one detailed map (st.map will only get you partial credit) – for full credit, include dots, icons, text that appears when hovering over a marker, or other map features
def crashmap():
    st.header(":green[Map Of Crashes in Massachusetts]", divider="rainbow")

    # Creating the dropdown to select county
    county_options = df['CNTY_NAME'].dropna().unique()
    county_options = ['All Counties'] + list(county_options)

    # [ST1] At least three Streamlit different widgets  (sliders, drop downs, multi-selects, text box, etc)
    selected_county = st.selectbox("Select a County:", options=county_options)

    # [DA4] Filtering data by one condition
    if selected_county == 'All Counties':
        df_filtered = df
    else:
        df_filtered = df[df['CNTY_NAME'] == selected_county]

    # List of columns to be used from the DataFrame
    mapdata = ["CRASH_NUMB", "CITY_TOWN_NAME", "CRASH_DATE_TEXT", "WEATH_COND_DESCR", "CRASH_TIME", "CRASH_STATUS",
               "CRASH_SEVERITY_DESCR", "NUMB_VEHC", "MANR_COLL_DESCR", "LAT", "LON", "STREETNAME", "STREET_NUMB"]
    dfMap = df_filtered.loc[:, mapdata]
    dfMap = dfMap.dropna(subset=mapdata)

    # Sets the initial view state of the map
    view_crashes = pdk.ViewState(
        latitude=dfMap["LAT"].mean(),
        longitude=dfMap["LON"].mean(),
        zoom=12,
        pitch=0)

    # Creates the backboard of information when hovering over a data point
    tooltip = {"html":
                   "Location: <b>{STREET_NUMB} {STREETNAME}, {CITY_TOWN_NAME}</b></br>"
                   "Date: <b>{CRASH_DATE_TEXT}</b><br/>"
                   "Crash Time: <b>{CRASH_TIME}</b><br/>"
                   "Weather Conditions: <b>{WEATH_COND_DESCR}</b></br>"
                   "Vehicles Involved: <b>{NUMB_VEHC}</b><br/>"
                   "Severity:  <b>{CRASH_SEVERITY_DESCR}</b><br/>"
                   "Crash Description: <b>{MANR_COLL_DESCR}</b><br/>",
               "style": {"backgroundColor": "rgba(135, 135, 227, 0.8)",
                         "color": "black"}}

    # Plotting the data points on the map
    data_points = pdk.Layer(
        "ScatterplotLayer",
        data=dfMap,
        get_position="[LON, LAT]",
        get_radius=50,
        auto_highlight=True,
        get_color=[3, 27, 145],
        pickable=True)

    # Combining everything into a Deck to be rendered by Streamlit
    crashmap = pdk.Deck(
        map_style="light",
        initial_view_state=view_crashes,
        layers=[data_points],
        tooltip=tooltip)

    st.pydeck_chart(crashmap)

# [PY1] A function with two or more parameters, one of which has a default value
# [DA5] Filtering data by two or more conditions with AND or OR
def filter_data(cities, severities=['Non-fatal injury']):
    return df[df['CITY_TOWN_NAME'].isin(cities) & df['CRASH_SEVERITY_DESCR'].isin(severities)]

# Function to create and display a bar chart visualizing crash severity data
# [VIZ1] At least three different types of charts with titles, colors, labels, legends, as appropriate
def severity_analysis_charts():
    # Streamlit UI components for Bar Chart
    st.header(":green[Crash Severity in Selected Cities/Towns]", divider="rainbow")

    # Retrieve unique city/town names from the DataFrame and set default selections
    city_town_options = df['CITY_TOWN_NAME'].unique()
    severity_options = ["Non-fatal injury", "Fatal injury","Property damage only (none injured)"]

    # [PY4] Using a list comprehension to filter and create a list of default city/town selections
    city_town_default = [city for city in ["BOSTON", "WALTHAM"] if city in city_town_options]
    severity_default = ["Non-fatal injury"] if "Non-fatal injury" in severity_options else []

    # Multiselect widget for selecting cities/towns and severity options
    # [ST2] At least three Streamlit different widgets  (sliders, drop downs, multi-selects, text box, etc)
    selected_city_town = st.multiselect("Select City/Town:", options=city_town_options, default=city_town_default)
    selected_severity = st.multiselect("Select Severity:", options=severity_options, default=severity_default)

    # Apply filters
    filtered_df = filter_data(selected_city_town, selected_severity)

    # Create a pivot table to reorganize filtered data for visualization and show multiple bars
    # [DA6] Analyzing data with pivot tables
    pivot_table = filtered_df.pivot_table(index='CITY_TOWN_NAME', columns='CRASH_SEVERITY_DESCR', aggfunc='size', fill_value=0)

    # Creating and displaying the first chart
    plt.figure(figsize=(10, 6))
    pivot_table.plot(kind='bar')
    plt.xlabel('City/Town')
    plt.ylabel('Number of Crashes')
    plt.title('Number of Crashes by City/Town and Severity')
    plt.xticks(rotation=45)
    plt.legend(title="Severity", title_fontsize='13', loc='upper right')
    st.pyplot()
    plt.clf()

    # Creating and displaying the second chart
    st.header(":green[Crash Severity in Selected Cities/Towns by the Hour]", divider="rainbow")

    # [DA7] Add / drop / select / create new / group columns, frequency count, other features
    # [DA9] Adding a new column to a DataFrame or performing calculations on DataFrame columns
    filtered_df['CRASH_HOUR'] = pd.to_datetime(filtered_df['CRASH_TIME'], format='%I:%M %p').dt.hour

    # Pivot table to organize data by both hour and city/town
    pivot_table_hour_city = filtered_df.pivot_table(index='CRASH_HOUR',columns=['CITY_TOWN_NAME', 'CRASH_SEVERITY_DESCR'],values='CRASH_NUMB', aggfunc='count', fill_value=0)

    # Plotting the data
    plt.figure(figsize=(10, 6))
    pivot_table_hour_city.plot(kind='bar', width=0.8)
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Crashes')
    plt.title('Crash Frequency by Hour and City/Town')
    plt.xticks(rotation=0)
    plt.legend(title="City/Town and Severity", title_fontsize='10', loc='upper right')
    st.pyplot()
    plt.clf()

    # Creating and displaying the third chart
    st.header(":green[Overall Crash Frequency by Hour]", divider="rainbow")
    df['CRASH_HOUR'] = pd.to_datetime(df['CRASH_TIME'], format='%I:%M %p').dt.hour

    # Plotting the data
    # [VIZ2] At least three different types of charts with titles, colors, labels, legends, as appropriate
    hour_crash_count = df['CRASH_HOUR'].value_counts().sort_index()
    st.line_chart(hour_crash_count)
    st.dataframe(hour_crash_count)



# [VIZ3] At least three different types of charts with titles, colors, labels, legends, as appropriate
def crash_cause():

    # Plotting the first pie chart
    st.header(":green[Overall Analysis of Crash Causes]", divider="rainbow")

    # [DA2] Sorting data in ascending or descending order
    crash_causes = df['MANR_COLL_DESCR'].value_counts().sort_values(ascending=False)

    # [DA3] Top largest or smallest values of a column
    top_crash_causes = crash_causes.head(3)
    plt.figure(figsize=(12, 10))
    plt.pie(crash_causes, labels=crash_causes.index, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('Proportion of Different Crash Causes')
    st.pyplot()
    plt.clf()

    # [PY2] A function that returns more than one value
    return crash_causes, top_crash_causes


def filtered_crash_cause():
    # Plotting the second pie chart
    st.header(":green[Analysis of Crash Causes by City/Town]", divider="rainbow")
    city_town_options = df['CITY_TOWN_NAME'].dropna().unique()
    selected_city = st.selectbox("Select a City/Town:", options=city_town_options)

    # Filtering the data based on the selected town/city
    filtered_df = df[df['CITY_TOWN_NAME'] == selected_city]
    crash_causes = filtered_df['MANR_COLL_DESCR'].value_counts()

    # Creating and plotting the data
    plt.figure(figsize=(8, 6))
    plt.pie(crash_causes, labels=crash_causes.index, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title(f'Proportion of Different Crash Causes in {selected_city}')
    st.pyplot()
    plt.clf()



# Navigation on streamlit webpage - (https://www.youtube.com/watch?v=hEPoto5xp3k)
def sidebar():
    with st.sidebar:
        # [ST3] At least three Streamlit different widgets  (sliders, drop downs, multi-selects, text box, etc)
        selected = option_menu(
            menu_title="Crash Zone",
            options=["Crash Map","Crash Severity Analysis","Crash Causes"],
            icons=["car-front","bar-chart","pie-chart"],
            styles = {
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {
                    "font-size": "18px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "green"},
            },
            )

    if selected == "Crash Map":
        st.title("Overview of Massachusetts Car Crashes")
        st.write("This section provides a visual map highlighting the locations of car crashes in Massachusetts for the year 2017. Explore the map to see detailed information on each crash, including severity, conditions, and more.")
        crashmap()
    elif selected == "Crash Severity Analysis":
        st.title("Detailed Crash Severity Analysis")
        st.write("This section allows you to filter the data based on city/town and severity to see detailed bar charts showing the distribution of crash severities.")
        severity_analysis_charts()
    if selected == "Crash Causes":
        st.title("Analysis of Crash Causes")
        st.write("This section provides insights into the causes of crashes. You can view an overall pie chart of crash causes or filter by city/town to see specific distributions of crash causes in different locations.")
        all_causes, top_causes = crash_cause()
        st.write("All Crash Causes:", all_causes)

        # [DA3] Top largest or smallest values of a column
        st.write("Top 3 Crash Causes:", top_causes)
        filtered_crash_cause()

def main():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Massachusetts Crashes in 2017")
    sidebar()

main()
