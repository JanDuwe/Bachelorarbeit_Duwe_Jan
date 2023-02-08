import names
import pandas as pd
import numpy as np
import sqlite3


def generateRandomStudents():
    """Generiert 100 zufällige Schüler mit zugehörigen GitHub Accounts, Vornamen, Nachnamen und E-Mail Adressen"""

    student_dict = {'gitHubAccount': [], 'firstName': [], 'lastName': [], 'eMail': []}

    for i in range(1, 101):
        firstName = names.get_first_name()
        lastName = names.get_last_name()
        gitHubAccount = firstName + lastName + str(np.random.randint(low=100, high=1000, size=1)[0])
        eMail = firstName + "." +lastName + "@sample.com"

        student_dict['gitHubAccount'].append(gitHubAccount)
        student_dict['firstName'].append(firstName)
        student_dict['lastName'].append(lastName)
        student_dict['eMail'].append(eMail)

    student_df = pd.DataFrame(columns=['gitHubAccount', 'firstName', 'lastName', 'eMail'], data=student_dict)

    return student_df

def generateAssignments():
    """Generiert 6 Aufgaben mit id, Namen und maximaler Punktzahl."""

    assignment_dict = {'id': [0, 1, 2, 3, 4, 5], 'name': ['Übung 1', 'Übung 2', 'Übung 3', 'Übung 4', 'Übung 5', 'Übung 6'], 'maxPoints': [100, 100, 100, 100,100, 100]}
    assignment_df = pd.DataFrame(columns=['id', 'name', 'maxPoints'], data=assignment_dict)

    return assignment_df

def generateRandomGradings(students, assignments):
    """Generiert zufällige Ergebnisse für zuvor generierte Schüler auf allen 6 Aufgaben."""

    grading_dict = {'student_GitHubAccount': [], 'assignment_id': [], 'reachedPoints': []}

    for assignment in assignments.index:
        a_id = assignments.loc[assignment, 'id']

        for row in students.index:
            gitHubAcc = students.loc[row, 'gitHubAccount']
            #TO-DO: muss getestet werden ob das auch so klappt
            reachedPoints = np.random.randint(low=0, high=assignments.loc[assignment, 'maxPoints']+1, size=1)

            grading_dict['assignment_id'].append(a_id)
            grading_dict['reachedPoints'].append(reachedPoints)
            grading_dict['student_GitHubAccount'].append(gitHubAcc)

    grading_df = pd.DataFrame(columns=['student_GitHubAccount', 'assignment_id', 'reachedPoints'], data=grading_dict)

    return grading_df