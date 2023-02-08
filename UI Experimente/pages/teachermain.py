import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import sys
import sqlite3

from scipy.stats import norm
import matplotlib.pyplot as plt

from sklearn import preprocessing

sys.path.append('C:/Users/Jan/Documents/VS Code Projects/Bachelorarbeit_Duwe_Jan/Daten')
from database_setup import *

st.set_page_config(layout="wide")
@st.cache
def doSomething():
    return ''

conn = sqlite3.connect('students.db')
c = conn.cursor()

st.title("Eine Sample Seite die meine Sampledaten aus der SampleDB anzeigt, danach noch eine Seite mit den echten Werten. Hier will ich nach Assignment filtern für epic Interaktivität")

#df = pd.read_csv('pages/a.csv')

#df_test = pd.read_csv('pages/StudentTestAccountDuwe_new_assignment_failed.csv')

#df = pd.concat([df, df_test])

d = {'Assignment_ID': ['Lesson 1', 'Lesson 2', 'Lesson 3','Lesson 1', 'Lesson 2', 'Lesson 3'],'Student_ID': ['StudentTestAccountDuwe', 'StudentTestAccountDuwe', 'StudentTestAccountDuwe', 'StudentTestAccountDuwe', 'StudentTestAccountDuwe', 'StudentTestAccountDuwe'],'Points': ['2', '4', '6', '5', '8', '6']}
df = pd.DataFrame(data=d)


c = alt.Chart(df).mark_bar(opacity=0.3, width=20).encode(
    x='Assignment_ID',
    y=alt.Y('Points:Q', stack=None),
    color='Student_ID',
)

#print(df)
#st.title(df.loc[df.index[0], 'Student_ID'])
#st.altair_chart(c, use_container_width=True)

st.title('Übersicht Übung 1 Dummy Data')
df_dummy_data = pd.read_csv('pages/dummydaten_BA_provisorisch_montag.csv')
df_dummy_data['Schüler'] = df_dummy_data['Nachname'] + ', ' +  df_dummy_data['Name']

#sort by amount of points reached in total
bellcurve_dummy = df_dummy_data.pivot_table(columns=['Erreichte Punkte'], aggfunc='size')
df_aggregated_results = pd.DataFrame(bellcurve_dummy, columns=['Erreichte Punkte'])


test = df_dummy_data['Erreichte Punkte'].value_counts()

myList = range(1,13)
df_aggregated_results['Erreichbare Punkte'] = myList

#print(df_dummy_data.mean())
#print(df_dummy_data.std())

chart_dummy_data = alt.Chart(df_dummy_data).mark_bar(opacity=1, width=5).encode(
    x='Schüler:N',
    y='Erreichte Punkte'
)

rule = alt.Chart(df_dummy_data).mark_rule(opacity=0.8, color='red').encode(
    y='mean(Erreichte Punkte)'
)

st.altair_chart(chart_dummy_data + rule, use_container_width=True)


bellcurve_chart = alt.Chart(df_aggregated_results).mark_bar().encode(
    x = 'Erreichbare Punkte',
    y = 'Erreichte Punkte'
)
#.properties(width=200, height=600)

st.altair_chart(bellcurve_chart, use_container_width=False)


fig, ax = plt.subplots(1,1)

#x = np.array(df_dummy_data['Erreichte Punkte'].tolist())
#x.sort()
#normalized_x = preprocessing.normalize([x])
x = np.linspace(norm.ppf(0.01), norm.ppf(0.99), 100)

sample_plot = ax.plot(x, norm.pdf(x),
        'r-', lw=5, alpha=0.6, label='norm pdf')

st.pyplot(fig=fig)
