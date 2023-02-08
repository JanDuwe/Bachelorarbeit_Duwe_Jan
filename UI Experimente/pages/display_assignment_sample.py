import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
#from streamlit_vega_lite import vega_lite_component, altair_component


import sys, os
from definitions import ROOT_DIR

st.write(ROOT_DIR)


sys.path.append(os.path.join(ROOT_DIR, 'Daten'))
#sys.path.append('C:/Users/Jan/Documents/VS Code Projects/Bachelorarbeit_Duwe_Jan/Daten')
from database_setup import *
from generate_sampledata import *


conn = sqlite3.connect('students_sampledata.db')
c = conn.cursor()

#st.set_page_config(layout="wide")

firstTimeSetup(conn)

getAllAssignmentsIDsAndNamesAsList(conn, c)

topColumns = st.empty()

with topColumns.container():
    selection_container, mean_container, std_container = st.columns(3, gap="large")

with selection_container:
    selected_assignment = st.selectbox("Übung auswählen:", getAllAssignmentsIDsAndNamesAsList(conn, c))
    df_display_all = getAllResultsPerAssignmentAsDF(conn, c, selected_assignment.split(':')[0])

with mean_container:
    st.write("Durchschnittliches Übungsergebnis:")
    mean = df_display_all['erreichte Punkte'].mean()
    st.write(mean)

with std_container:
    st.write("Standardabweichung:")
    std = df_display_all['erreichte Punkte'].std()
    st.write(std)



maxPoints = df_display_all.loc[0, 'Maximalpunkte']

chart_display_all = alt.Chart(df_display_all).mark_bar(opacity=1, width=5, tooltip=True).encode(
    x=alt.X('Name', sort='-x'),
    y= alt.Y('erreichte Punkte', sort="y")
).interactive()

rule = alt.Chart(df_display_all).mark_rule(opacity=0.8, color='red').encode(
    y='mean(erreichte Punkte)'
)

st.header("Alle Schüler auf einen Blick inkl. Mittelwert")
st.altair_chart(chart_display_all + rule, use_container_width=True)

df_display_reached_points_name = df_display_all.drop(['id', 'Übung', 'Maximalpunkte'], axis=1)

chart_test = alt.Chart(df_display_reached_points_name).mark_bar(opacity=1, width=5).encode(
    x=alt.X('Range', sort=alt.EncodingSortField(op='count', order='ascending')),
    y=alt.Y('count()', type='quantitative', axis=alt.Axis(tickMinStep=1))
)

brush = alt.selection(type='interval', encodings=['x'])

interactive_test = alt.Chart(df_display_reached_points_name).mark_bar(opacity=1).encode(
    x= alt.X('erreichte Punkte', scale=alt.Scale(domain=[0, maxPoints]), bin=True),
    y=alt.Y('count()', type='quantitative', axis=alt.Axis(tickMinStep=1), title='Anzahl Schüler'),
    color = alt.Color('Name', legend=None, scale=alt.Scale(scheme='blues'))
).properties(width=900)

upper = interactive_test.encode(
    alt.X('erreichte Punkte', sort=alt.EncodingSortField(op='count', order='ascending'), scale=alt.Scale(domain=brush), bin=True),
    tooltip=[alt.Tooltip('erreichte Punkte', title='Punkte'),alt.Tooltip('Name')]

)

lower = interactive_test.properties(
    height=60
).add_selection(brush)

concat_distribution_interactive = alt.vconcat(upper, lower)


st.header("Verteilung der Übungsergebnisse")
st.altair_chart(concat_distribution_interactive, use_container_width=True)


#st.table(df_display_all)

result_count = countAllResults(df_display_all)

result_count_chart = alt.Chart(result_count).mark_bar().encode(
    x = 'Maximalpunkte',
    y = 'Erreichte Punkte'
)
#.properties(width=200, height=600)

#st.altair_chart(result_count_chart, use_container_width=False)


st.header("Wahrscheinlichkeitsverteilung der Ergebnisse")

chart = alt.Chart(df_display_reached_points_name).transform_density(
    'erreichte Punkte',
    as_=['erreichte Punkte', 'density'],
    #bandwidth=1
).mark_area().encode(
    alt.X("erreichte Punkte:Q"),
    y='density:Q',
).properties(
    width=900
)

st.altair_chart(chart, use_container_width=False)


#st.write("damit erweitern? https://dst-ws22.github.io/website/code/altair/44-altair_interaction_p.html#details-on-demand")

#st.write("ausprobieren was passiert wenn ich meine datenverteilung damit anzeige https://mr-ws22.github.io/website/code/59-mathematical.html")

#st.write("interessant für count https://vega.github.io/vega-lite/docs/aggregate.html")