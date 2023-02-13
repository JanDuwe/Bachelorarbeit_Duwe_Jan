import sqlite3
import csv
import pandas as pd

from api import *
from generate_sampledata import *

import sys
sys.path.append('C:/Users/Jan/Documents/VS Code Projects/Bachelorarbeit_Duwe_Jan/Daten')



def firstTimeSetup(connection):
    """Erstellt die Datenbanktabellen nach dem ER-Modell."""
    try:
        with connection:
            connection.execute("""CREATE TABLE student (
                gitHubAccount TEXT PRIMARY KEY,
                firstName TEXT,
                lastName TEXT,
                eMail TEXT
            )""")

            connection.execute("""CREATE TABLE assignment (
                id INTEGER PRIMARY KEY,
                name TEXT,
                inviteLink TEXT,
                maxPoints INTEGER
            )""")

            connection.execute("""CREATE TABLE grading (
                student_gitHubAccount TEXT,
                assignment_id INTEGER,
                reachedPoints INTEGER,
                FOREIGN KEY(student_gitHubAccount) REFERENCES student(gitHubAccount),
                FOREIGN KEY(assignment_id) REFERENCES assignment(id)
            )""")
    
    except:
        pass


def getStudentsFromCsvToSQLite(path_to_csv, connection):
    """Implementiert den Import von Schülern aus einer CSV Datei in der Ansicht Verwaltung. Hinterlegt dabei die Schüler in der DB."""
    df = pd.read_csv(path_to_csv)
    df.rename(columns={'name': 'firstName'}, inplace=True)
    df.rename(columns={'github_username': 'gitHubAccount'}, inplace=True)

    with connection:
        connection.execute("DROP TABLE student")
        connection.execute("""CREATE TABLE student (
                                gitHubAccount TEXT PRIMARY KEY,
                                firstName TEXT,
                                lastName TEXT,
                                eMail TEXT
                                )""")

    for row in df.index:
        df.loc[row, 'lastName'] = df.loc[row, 'firstName'].split()[1]
        df.loc[row, 'firstName'] = df.loc[row, 'firstName'].split()[0]

        gitHubAccount = df.loc[row, 'gitHubAccount']
        firstName = df.loc[row, 'firstName']
        lastName = df.loc[row, 'lastName']
        eMail = getStudentsEmail(df.loc[row, 'gitHubAccount'])

        with connection:
            connection.execute("INSERT INTO student VALUES(:gitHubAccount, :firstName, :lastName, :eMail)", 
            {'gitHubAccount': gitHubAccount, 'firstName': firstName, 'lastName':lastName, 'eMail': eMail})

def getAllStudentsAsDF(connection, cursor):
    """Führt ein SQL Statement aus das alle Eintrage der Tabelle 'student' zurückgibt im DataFrame Format."""
    with connection:
        cursor.execute("""SELECT * FROM student""")

        df = pd.DataFrame(
            data=cursor.fetchall(),
            columns=['GitHub Username', 'Vorname', 'Name', 'E-Mail']
        )
        df.index += 1
    return df

def loadSampleDataIntoDB(connection, cursor, students, assignments, gradings):
    """Liest die generierten Sample Daten aus 'generate_sampledata.py' in die SQLite Datenbank ein."""

    for row in students.index:
        firstName = students.loc[row, 'firstName']
        lastName = students.loc[row, 'lastName']
        gitHubAccount = students.loc[row, 'gitHubAccount']
        eMail = students.loc[row, 'eMail']

        with connection:
            cursor.execute("INSERT INTO student VALUES(:gitHubAccount, :firstName, :lastName, :eMail)", 
            {'gitHubAccount': gitHubAccount, 'firstName': firstName, 'lastName':lastName, 'eMail': eMail})


    for row in assignments.index:
        a_id = assignments.loc[row, 'id'].item()
        name = assignments.loc[row, 'name']
        maxPoints = assignments.loc[row, 'maxPoints'].item()

        with connection:
            cursor.execute("INSERT INTO assignment VALUES(:id, :name, :maxPoints)", 
            {'id': a_id, 'name': name, 'maxPoints': maxPoints})

    for row in gradings.index:
        assignment_id = gradings.loc[row, 'assignment_id'].item()
        reachedPoints = gradings.loc[row, 'reachedPoints'].item()
        student_GitHubAccount = gradings.loc[row, 'student_GitHubAccount']

        with connection:
            cursor.execute("INSERT INTO grading VALUES(:student_GitHubAccount, :assignment_id, :reachedPoints)", 
            {'student_GitHubAccount': student_GitHubAccount, 'assignment_id': assignment_id, 'reachedPoints': reachedPoints})


        
def getAllStudentNamesAsList(connection, cursor):
    """Wählt alle Schülernamen aus der Tabelle 'student' und gibt sie formatiert gemeinsam mit dem GitHub Usernamen als Liste zurück."""
    with connection:
        cursor.execute("SELECT firstName, lastName, gitHubAccount FROM student")
        temp = cursor.fetchall()
        result = []
        for name in temp:
            concat_name = ''
            concat_name = name[-1] + ": " + name[0] + " " + name[1]
            result.append(concat_name)

    return result

def getAllGradesPerStudent(connection, cursor, student):
    """Gibt alle Übungsergebnisse eines ausgewählten Schülers in einem Pandas DataFrame aus."""
    statement = """SELECT assignment.id, assignment.Name, gr.reachedPoints, assignment.maxPoints 
                    FROM grading as gr
                    LEFT JOIN assignment ON gr.assignment_id=assignment.id
                    WHERE gr.student_gitHubAccount = '""" + student + "'"
    
    with connection:
        cursor.execute(statement)
        temp = cursor.fetchall()

        result = pd.DataFrame(temp, columns=['id', 'übungsName', 'erreichtePunkte', 'maximalPunkte'])
    
    return result

def getAllGradesFromAllStudentsPerAssignmentAsList(connection, cursor, assignment):
    """Gibt alle Übungsergebnisse von allen Schülern als Python Listenobjekt aus."""

    with connection:
        cursor.execute("""SELECT assignment.Name, gr.reachedPoints, assignment.maxPoints 
                        FROM grading as gr
                        LEFT JOIN assignment ON gr.assignment_id=assignment.id
                        WHERE assignment.id = '""" + str(assignment) + "'")
        
        temp = cursor.fetchall()

        temp_df = pd.DataFrame(temp, columns=['übungsName', 'erreichtePunkte', 'maximalPunkte'])

        result = temp_df.erreichtePunkte.values.tolist()
        result.sort()

    return result

def getAllGrades(connection, cursor, assignment):
    """Gibt alle Ergebnisse einer Übung als DataFrame Objekt aus."""
    with connection:
        cursor.execute("""SELECT assignment.Name, gr.reachedPoints, assignment.maxPoints 
                        FROM grading as gr
                        LEFT JOIN assignment ON gr.assignment_id=assignment.id
                        WHERE assignment.id = '""" + str(assignment) + "'")
        
        temp = cursor.fetchall()

        temp_df = pd.DataFrame(temp, columns=['übungsName', 'erreichtePunkte', 'maximalPunkte'])

        return temp_df

def getPercentileFromList(student_result, assignment, result_list):
    """Gibt das Perzentil des Ergebnis eines Schülers von einer Übung als formatierter String zurück."""
    result_list.sort()
    percentile = 0
    better_than = 0

    while(student_result > result_list[better_than]):
        better_than = better_than + 1

    percentile = better_than*100//len(result_list)

    result = "Das Ergebnis in Übung " + str(assignment) + " ist im " + str(percentile) + """. Perzentil aller Abgaben."""
    return percentile
    

def getAllAssignmentsIDsAndNamesAsList(connection, cursor):
    """Gibt alle IDs und Namen von Übungen in der Datenbank als Python List Objekt zurück."""
    with connection:
        cursor.execute("""SELECT id, name
                        FROM assignment""")
        temp = cursor.fetchall()
        
        result = []

        for assignment in temp:
            concat_name = ''     
            concat_name = str(assignment[0]) + ":" + assignment[1]
            result.append(concat_name)

    return result   

def getAllResultsPerAssignmentAsDF(connection, cursor, assignmentID):
    """
    Gibt alle Ergebnisse pro Übung als DataFrame Objekt zurück.
    Folgende Attribute werden ebenfalls ausgegeben: ID, Name und maximale Punktzahl der Übung, Name des Schülers, erreichte Punkzahl.
    """
    statement = """SELECT assignment.id, assignment.name, student.firstName, student.LastName, gr.reachedPoints, assignment.maxPoints 
                    FROM grading as gr
                    LEFT JOIN assignment ON gr.assignment_id=assignment.id
                    LEFT JOIN student ON gr.student_gitHubAccount=student.gitHubAccount
                    WHERE assignment.id = '""" + assignmentID + "'"
    with connection:
        cursor.execute(statement)

        temp = cursor.fetchall()

    """Erstellt neue Liste an Tuples um den Vornamen und Nachnamen des Schülers in einer Spalte darzustellen."""
    result_list = []
    for element in temp:
        temptuple = (element[0], element[1], element[2] +  " " +  element[3], element[4], element[5])
        result_list.append(temptuple)

    result = pd.DataFrame(data=result_list, columns=['id', 'Übung', 'Name', 'erreichte Punkte', 'Maximalpunkte'])

    return result


def insertAssignmentIntoDB(connection, cursor, name, inviteLink, maxPoints):
    """Funktion um Übungen, die im Formular der Hauptseite angelegt wurden in der DB zu hinterlegen."""
    with connection:
            cursor.execute("INSERT INTO assignment VALUES(:id, :name, :inviteLink, :maxPoints)", 
            {'id': None, 'name': name, 'inviteLink': inviteLink, 'maxPoints': maxPoints})

            connection.commit()

def getAllAssignmentsNamesInviteLinksAsDF(connection, cursor):
    """Funktion um alle Übungsnamen und Einladungs URLs als DataFrame Objekt zu speichern."""
    with connection:
        cursor.execute("""SELECT name, inviteLink FROM assignment""")
        result = pd.DataFrame(cursor.fetchall(), columns=['Name', 'Einladungslink'])
        result.index += 1
    
    return result


def collectAllGradingsPerAssignment(connection, cursor, assignment_id, assignment_name):
    """Schreibt alle Übungsergebnisse von allen Schülern pro Übung in die SQLite Datenbank."""

    statement_delete = "DELETE FROM grading WHERE assignment_id = " + str(assignment_id)
    
    #get all students
    #call get getAssignmentResults() for all students 

    with connection:

        cursor.execute(statement_delete)
        connection.commit()

        student_names = getAllStudentNamesAsList(connection, cursor)

        for name in student_names:
            single_assignment_result = getAssignmentResults(name.split(':')[0], assignment_name)

            reached_points = single_assignment_result[2]

            cursor.execute("INSERT INTO grading VALUES(:student_GitHubAccount, :assignment_ID, :reachedPoints)",
            {'student_GitHubAccount':name.split(':')[0], 'assignment_ID': assignment_id, 'reachedPoints': reached_points})
            connection.commit()

def getAllAssignmentResultsGroupedByAssignment(connection, cursor):
    with connection:
        cursor.execute("""SELECT id
                        FROM assignment""")
        result = []
        result = cursor.fetchall()

        result_dict = {}
        for assignment in result:
            result_dict[int(''.join(map(str, assignment)))] = getAllGradesFromAllStudentsPerAssignmentAsList(connection, cursor, int(''.join(map(str, assignment))))
    return result_dict

def getAllPercentilesByStudent(student_results, connection, cursor):
    return_value = []
    with connection:
        for result in student_results['id']:
            statement = "SELECT reachedPoints FROM grading WHERE assignment_id = " + str(result)
            cursor.execute(statement)
            temp_all_results = cursor.fetchall()
            y = [i[0] for i in temp_all_results]
            return_value.append(getPercentileFromList(student_results.at[result, 'erreichtePunkte'], result, y))

    return return_value

def getMaxPointsByAssignment(assignment_id, connection, cursor):
    """Gibt die maximale Punktzahl einer Übung als Integer zurück"""
    statement = "SELECT maxPoints FROM assignment WHERE id = " + assignment_id
    with connection:
        cursor.execute(statement)
        temptuple = cursor.fetchall()[0]
        result = temptuple[0]

    return result

def getAssignmentNameByID(assignment_id, connection, cursor):
    """Gibt den Namen einer Übung basierend auf deren ID zurück."""
    statement = """SELECT name from assignment where id = """ + str(assignment_id)

    with connection:
        cursor.execute(statement)

        temp = cursor.fetchall()
    
    doubletemp = temp[0]
    result = doubletemp[0]
    
    return result

def getAllStudentsResultsByAssignmentID(assignment_id, connection, cursor):
    """Gibt den Namen einer Übung, den Namen eines Schülers und die erreichte Punktzahl als DataFrame Objekt zurück."""
    statement = """SELECT assignment.name, student.firstName, student.LastName, gr.reachedPoints
                    FROM grading as gr
                    LEFT JOIN assignment ON gr.assignment_id=assignment.id
                    LEFT JOIN student ON gr.student_gitHubAccount=student.gitHubAccount
                    WHERE assignment.id = '""" + assignment_id + "'"

    with connection:
        cursor.execute(statement)
        temp_result_list = cursor.fetchall()

    result = pd.DataFrame(temp_result_list, columns=['Übungsname', 'Vorname', 'Nachname', 'erreichte Punkte'])

    return result

def calculatePercentileForStudent(result_df):
    """Berechnet das Perzentil für einen Schüler."""
    result_list = result_df['erreichte Punkte'].tolist()
    result_list.sort()

    result_df['Perzentil'] = ""
    print(result_df)

    for index, row in result_df.iterrows():
        single_result = result_df.at[index, 'erreichte Punkte']
        print(single_result)
        better_than = 0
        

        while(single_result > result_list[better_than]):
            better_than = better_than + 1

        print("better than: " + str(better_than))

        percentile = better_than*100//len(result_list)
        print(percentile)
        result_df.at[index, 'Perzentil'] = percentile

    return result_df