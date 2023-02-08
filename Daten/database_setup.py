import sqlite3
import csv
import pandas as pd

from testapi import *
from generate_sampledata import *

import sys
sys.path.append('C:/Users/Jan/Documents/VS Code Projects/Bachelorarbeit_Duwe_Jan/Daten')


#set up the three mandatory tables
#only call if the tables do not exist yet
def firstTimeSetup(connection):
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

#TO-DO
#make this a function, this gives back students and their corresponding reached points of any assignment
#need to put this into a dataframe in order to display it on streamlit tho
def getPointsByAssignment(assignment, connection):
    with connection:
        connection.execute("""SELECT gr.student_gitHubAccount, gr.assignment_id, assignment.Name, gr.reachedPoints, assignment.maxPoints
                    FROM grading AS gr
                    LEFT JOIN assignment ON gr.assignment_id=assignment.id
                    """)


#student name has to have format "firstname:lastname" for this function to work, middle names are not supported
def getStudentsFromCsvToSQLite(path_to_csv, connection):

    #drop all tables when updating the classroom with a new csv file
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

#getStudentsFromCsvToMariaDB('Bachelorarbeit_Duwe_Jan/Daten/classroom_roster.csv')

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

def AconnectToDB():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

#connection.commit() fehlt hier? wieso wird das trotzdem geladen??
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
    ###METHODE SO UMSCHREIBEN DASS DIE ALLE ASSIGNMENT RESULTS PRO ASSIGNMENT GIBT!! ALS DICTIONARY KEY IST ASSIGNMENT ID UND VALUE DIE ERGEBNISSE ODER SO?
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
    ### UMSCHREIBEN DASS ES DEN ÜBUNGSNAMEN UND NICHT DIE ÜBUNGSID AUSGIBT
    ### VLLT AUCH AN DIE METHODE OBEN ANPASSEN DASS ICH ALLE ASSIGNMENTS FÜTTERN KANN UND DANN DIREKT ALLES AUSGEBE
    result_list.sort()
    percentile = 0
    better_than = 0

    while(student_result > result_list[better_than]):
        better_than = better_than + 1

    percentile = better_than*100//len(result_list)

    result = "Das Ergebnis in Übung " + str(assignment) + " ist im " + str(percentile) + """. Perzentil aller Abgaben."""
    return percentile
    

def getAssignmentIDFromDF(assignment, studentResults):
    """Gibt die gesuchte ID einer Übungsaufgabe aus einem DataFrame als Python Integer zurück. Die Variable assignment bestimmt nach welcher Übungsaufgabe gesucht wird."""


    return ""

def getAllAssignmentsIDsAndNamesAsList(connection, cursor):
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

def countAllResults(assignmentResults):
    temp = assignmentResults.pivot_table(columns=['erreichte Punkte'], aggfunc='size')

    result = pd.DataFrame(temp, columns=['erreichte Punkte'])
    return result

def insertAssignmentIntoDB(connection, cursor, name, inviteLink, maxPoints):
    with connection:
            cursor.execute("INSERT INTO assignment VALUES(:id, :name, :inviteLink, :maxPoints)", 
            {'id': None, 'name': name, 'inviteLink': inviteLink, 'maxPoints': maxPoints})

            connection.commit()

def getAllAssignmentsNamesInviteLinksAsDF(connection, cursor):
    with connection:
        cursor.execute("""SELECT name, inviteLink FROM assignment""")
        result = pd.DataFrame(cursor.fetchall(), columns=['name', 'inviteLink'])
        result.index += 1
    
    return result

def getAssignmentNameFromID(connection, cursor, assignment_id):
    statement = """SELECT name 
                    FROM assignment 
                    WHERE id=""" + assignment_id
    
    with connection:
        cursor.execute(statement)
        result = cursor.fetchall()

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
    #all_results = getAllAssignmentResultsGroupedByAssignment(connection, cursor)
    #return_value = ""
    #for key in all_results:
    #    return_value = return_value + getPercentileFromList(student_results[key], key, all_results[key]) + "\n"
    return_value = []
    with connection:
        for result in student_results['id']:
            #print(result)
            statement = "SELECT reachedPoints FROM grading WHERE assignment_id = " + str(result)
            cursor.execute(statement)
            temp_all_results = cursor.fetchall()
            #print("hello")
            #convert list of tuples to list of int
            y = [i[0] for i in temp_all_results]
            #print(y)
            return_value.append(getPercentileFromList(student_results.at[result, 'erreichtePunkte'], result, y))

    return return_value

def getMaxPointsByAssignment(assignment_id, connection, cursor):
    statement = "SELECT maxPoints FROM assignment WHERE id = " + assignment_id
    with connection:
        cursor.execute(statement)
        temptuple = cursor.fetchall()[0]
        result = temptuple[0]

    return result

def getAssignmentNameByID(assignment_id, connection, cursor):

    statement = """SELECT name from assignment where id = """ + str(assignment_id)

    with connection:
        cursor.execute(statement)

        temp = cursor.fetchall()
    
    doubletemp = temp[0]
    result = doubletemp[0]
    
    return result

def getAllStudentsResultsByAssignmentID(assignment_id, connection, cursor):
    
    statement = """SELECT assignment.name, student.firstName, student.LastName, gr.reachedPoints
                    FROM grading as gr
                    LEFT JOIN assignment ON gr.assignment_id=assignment.id
                    LEFT JOIN student ON gr.student_gitHubAccount=student.gitHubAccount
                    WHERE assignment.id = '""" + assignment_id + "'"

    with connection:
        cursor.execute(statement)
        temp_result_list = cursor.fetchall()

    result = pd.DataFrame(temp_result_list, columns=['Übungsname', 'Vorname', 'Nachname', 'erreichte Punkte'])

    print(result)

    return result

def calculateSinglePercentileForStudent(result_df):
    
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

def getAllReachedPointsByAssignmentID(assignment_id, connection, cursor):
    
    statement = "SELECT reachedPoints FROM grading WHERE assignment_id = " + str(assignment_id)

    with connection:
        cursor.execute(statement)
        result = cursor.fetchall()

    return result
