import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

import sys, os
sys.path.append('C:/Users/Jan/Documents/VS Code Projects/Bachelorarbeit_Duwe_Jan/Daten')
from database_setup import *
from generate_sampledata import *


conn = sqlite3.connect('students.db')
c = conn.cursor()

firstTimeSetup(conn)


df = getAllStudentsAsDF(conn, c)

st.set_page_config(layout="wide")
st.title("Statistiken zu einzelnen Schülern")

selectedStudent = st.selectbox("Einzelnen Schüler auswählen:", getAllStudentNamesAsList(conn, c))

studentResults = getAllGradesPerStudent(conn, c, str(selectedStudent.split(":")[0]))
student_histogram = alt.Chart(studentResults).mark_bar().encode(
    x=('übungsName'),
    y=('erreichtePunkte')
).properties(width=350)

placeholder = st.empty()

with placeholder.container():
    histogram_container, table_container, percentile_container = st.columns(3)

histogram_container.altair_chart(student_histogram)

table_container.write(studentResults)

#notiz in database_setup.py beachten, so ist das gerade hässlich
#

percentile_container.write(getAllAssignmentResultsGroupedByAssignment(conn, c))
st.write("quartile bzw position im quartil implementieren")
st.write("interaktives diagram bei dem ich übung pro schüler auswählen kann und die aktuelle position (im quartil) anzeige")
st.write("darunter dann in welchem percentile der schüler sich bei der übung befindet")


#st.table(ass1_results)