import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import sys, os
from jinja2 import Environment, FileSystemLoader

from definitions import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, 'Daten'))

from datahandler import *

####### Generelles Setup der Seite

st.set_page_config(layout="wide")

conn = sqlite3.connect('students.db')
c = conn.cursor()

firstTimeSetup(conn)

st.markdown('<style>h1{text-align: center;}</style>', unsafe_allow_html=True)
st.title('Verwaltung')

all_students_df = getAllStudentsAsDF(conn, c)

####### Erstellen der Container Elemente

student_container, assignment_container, grading_container = st.columns(3)

####### Übersicht des Klassenzimmers 

with student_container:
    st.header("Übersicht Klassenzimmer")
    placeholder_roster = st.empty()

    if (all_students_df.index.size==0):
        placeholder_roster.write("Noch keine Schüler vorhanden, bitte laden Sie eine CSV mit Schülerdaten hoch.")

    display_student_table = st.table(all_students_df)

    uploaded_csv = st.file_uploader("Klassenzimmer aktualisieren:")

    if (uploaded_csv != None):
        getStudentsFromCsvToSQLite(uploaded_csv, conn)
        all_students_df = getAllStudentsAsDF(conn, c)
        display_student_table.table(all_students_df)
        placeholder_roster.empty()

####### Übersicht der Übungen

with assignment_container:
    st.header("Übersicht Übungen")

    all_assignments_df = getAllAssignmentsNamesInviteLinksAsDF(conn, c)

    placeholder_assignments = st.empty()

    if (all_assignments_df.index.size==0):
        placeholder_assignments.write("Noch sind keine Übungen vorhanden, bitte tragen Sie diese im unteren Formular ein.")

    display_assignment_table = st.table(all_assignments_df)

    with st.form("my_form"):
        assignment_name = st.text_input("Bitte den Namen der Übung eintragen.")
        assignment_invite_link = st.text_input("Bitte den Einladungslink der Übung eintragen.")
        assignment_max_points = st.number_input("Bitte die maximal zu erreichenden Punkte der Übung eintragen.", step=1)

        submitted = st.form_submit_button("Submit")
        if submitted:
            insertAssignmentIntoDB(conn, c, assignment_name, assignment_invite_link, assignment_max_points)
            all_assignments_df = getAllAssignmentsNamesInviteLinksAsDF(conn, c)
            display_assignment_table.table(all_assignments_df)
            placeholder_assignments.empty()

####### Ergebnisse kommunizieren

with grading_container:
    st.header("Ergebnisse kommunizieren")
    selection = st.selectbox('Übung auswählen', getAllAssignmentsIDsAndNamesAsList(conn, c))
    if st.button("Bestätigen"):
        max_points = getMaxPointsByAssignment(selection.split(':')[0], conn, c)
        #all_results_by_assignment = getAllReachedPointsByAssignmentID(selection.split(':')[0], conn, c)
        assignment_name = selection.split(':')[1]

        all_results_df = getAllStudentsResultsByAssignmentID(selection.split(':')[0], conn, c)
        
        all_percentiles_df = calculatePercentileForStudent(all_results_df)
        st.write(all_percentiles_df)

        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template("myTemplate.txt")

        for index, row in all_percentiles_df.iterrows():
            file_name = assignment_name + "_" + all_percentiles_df.at[index, 'Vorname'] + "_" + all_percentiles_df.at[index, 'Nachname']
            filename = f"messages/message_{file_name.lower()}.txt"
            content = template.render(
                vorname = all_percentiles_df.at[index, 'Vorname'],
                nachname = all_percentiles_df.at[index, 'Nachname'],
                reached_points = all_percentiles_df.at[index, 'erreichte Punkte'],
                percentile = all_percentiles_df.at[index, 'Perzentil'],
                maxpoints=max_points,
                test_name=assignment_name
            )
            with open(filename, mode="w", encoding="utf-8") as message:
                message.write(content)
                print(f"... wrote {filename}")