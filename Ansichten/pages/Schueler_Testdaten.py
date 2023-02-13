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

conn = sqlite3.connect('students_sampledata.db')
c = conn.cursor()

firstTimeSetup(conn)

df = getAllStudentsAsDF(conn, c)

st.set_page_config(layout="wide")
st.title("Statistiken zu einzelnen Schülern")

####### Funktionalität um Testdaten zu laden. Gibt kein Feedback in der Oberfläche, nicht öfter als 1 Mal ausführen

if st.button('load sample data'):
    assignments = generateAssignments()
    students = generateRandomStudents()
    grading = generateRandomGradings(students=students, assignments=assignments)
    loadSampleDataIntoDB(conn, c, students, assignments, grading)


####### Auswahl, welcher Schüler dargestellt werden soll

selectedStudent = st.selectbox("Einzelnen Schüler auswählen:", getAllStudentNamesAsList(conn, c))

####### Definieren der Container der Darstellung

placeholder = st.empty()

with placeholder.container():
    barchart_container, table_container, percentile_container = st.columns(3)

####### Notwendigen Daten laden

studentResults = getAllGradesPerStudent(conn, c, str(selectedStudent.split(":")[0]))

####### Barchart der Ergebnisse eines Schülers erstellen

student_results_barchart = alt.Chart(studentResults).mark_bar().encode(
    x=('übungsName'),
    y=('erreichtePunkte')
).properties(width=350)

barchart_container.altair_chart(student_results_barchart)

####### Tabellarische Darstellung der Daten

table_container.write(studentResults)

####### Berechnung und darstellen der Perzentile

concat_percentiles = ""
for i, value in enumerate(getAllPercentilesByStudent(studentResults, conn, c)):
    concat_percentiles = concat_percentiles + "Das Ergebnis in "+ str(getAssignmentNameByID(i, conn, c)) + " befindet sich im " +  str(value) + ". Perzentil." + "\n\n"

percentile_container.write(concat_percentiles)