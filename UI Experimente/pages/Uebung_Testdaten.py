import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

import sys, os
from definitions import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, 'Daten'))
from datahandler import *
from generate_sampledata import *

####### Generelles Setup der Seite
st.set_page_config(layout="wide")
conn = sqlite3.connect('students_sampledata.db')
c = conn.cursor()

firstTimeSetup(conn)

getAllAssignmentsIDsAndNamesAsList(conn, c)

####### Erstellen der Container Elemente

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


####### Überblick der Schüler

maxPoints = df_display_all.loc[0, 'Maximalpunkte']

chart_display_all = alt.Chart(df_display_all).mark_bar(opacity=1, width=5, tooltip=True).encode(
    x=alt.X('Name'),
    y= alt.Y('erreichte Punkte', sort="y")
).interactive()

rule = alt.Chart(df_display_all).mark_rule(opacity=0.8, color='red').encode(
    y='mean(erreichte Punkte)'
)

st.header("Alle Schüler auf einen Blick")
st.altair_chart(chart_display_all + rule, use_container_width=True)

df_display_reached_points_name = df_display_all.drop(['id', 'Übung', 'Maximalpunkte'], axis=1)

####### Histogramm der Ergebnisse, interaktiv

brush = alt.selection(type='interval', encodings=['x'])

distribution_results_interactive = alt.Chart(df_display_reached_points_name).mark_bar(opacity=1).encode(
    x= alt.X('erreichte Punkte', scale=alt.Scale(domain=[0, maxPoints]), bin=True),
    y=alt.Y('count()', type='quantitative', axis=alt.Axis(tickMinStep=1), title='Anzahl Schüler'),
    color = alt.Color('Name', legend=None, scale=alt.Scale(scheme='blues'))
).properties(width=900)

upper = distribution_results_interactive.encode(
    alt.X('erreichte Punkte', sort=alt.EncodingSortField(op='count', order='ascending'), scale=alt.Scale(domain=brush), bin=True),
    tooltip=[alt.Tooltip('erreichte Punkte', title='Punkte'),alt.Tooltip('Name')]

)

lower = distribution_results_interactive.properties(
    height=60
).add_selection(brush)

concat_distribution_interactive = alt.vconcat(upper, lower)

st.header("Verteilung der Übungsergebnisse")
st.altair_chart(concat_distribution_interactive, use_container_width=True)

####### Interaktives Diagramm der Wahrscheinlichkeitsfunktion

probability_selection = alt.selection(type='interval', encodings=['x'])

kernel_density_chart = alt.Chart(df_display_reached_points_name).transform_density(
    'erreichte Punkte',
    as_=['erreichte Punkte', 'density'],
    #bandwidth=1
).mark_area().encode(
    alt.X("erreichte Punkte:Q"),
    y='density:Q',
).properties(
    width=900
).add_selection(probability_selection)

text = alt.Chart(df_display_reached_points_name).transform_density(
    'erreichte Punkte',
    as_=['erreichte Punkte', 'density'],
).transform_filter(probability_selection).mark_text(
    align='left',
    baseline='top',
    color='white'
).encode(
    x=alt.value(5),
    y=alt.value(5),
    text=alt.Text('sum(density):Q', format='.4f'),
)

st.header("Wahrscheinlichkeitsfunktion der Ergebnisse")
st.altair_chart(kernel_density_chart + text, use_container_width=False)