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

conn = sqlite3.connect('students.db')
c = conn.cursor()

firstTimeSetup(conn)


df = getAllStudentsAsDF(conn, c)

st.set_page_config(layout="wide")
st.title("Statistiken zu einzelnen Schülern")

####### Auswahl, welcher Schüler dargestellt werden soll

selectedStudent = st.selectbox("Einzelnen Schüler auswählen:", getAllStudentNamesAsList(conn, c))

studentResults = getAllGradesPerStudent(conn, c, str(selectedStudent.split(":")[0]))

####### Definieren der Container der Darstellung

placeholder = st.empty()

with placeholder.container():
    histogram_container, table_container, percentile_container = st.columns(3)

####### Barchart der Ergebnisse eines Schülers erstellen

student_histogram = alt.Chart(studentResults).mark_bar().encode(
    x=('übungsName'),
    y=('erreichtePunkte')
).properties(width=350)

histogram_container.altair_chart(student_histogram)

####### Tabellarische Darstellung der Daten

table_container.write(studentResults)

####### Berechnung und darstellen der Perzentile

#percentile_container.write(getAllAssignmentResultsGroupedByAssignment(conn, c))
concat_percentiles = ""
for i, value in enumerate(getAllPercentilesByStudent(studentResults, conn, c)):
    concat_percentiles = concat_percentiles + "Das Ergebnis in "+ str(getAssignmentNameByID(i, conn, c)) + " befindet sich im " +  str(value) + ". Perzentil." + "\n\n"

percentile_container.write(concat_percentiles)