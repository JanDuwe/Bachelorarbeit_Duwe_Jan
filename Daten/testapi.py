from fileinput import filename
import requests
import csv
import re

#braucht dringend error handling falls übung nicht existiert!°!!!!!!!!!!!
def getAssignmentResults(studentGitHubAccount, assignment_name):
    url_github = "https://api.github.com/repos/JanDuweBachelorarbeit/" + assignment_name + "-" + studentGitHubAccount + "/contents/metadata_raw.csv"
    headers = {'Accept': 'application/vnd.github+json','Authorization': 'Bearer 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'}
    r_github = requests.get(url=url_github, headers=headers)

    url_resulting = r_github.json()['download_url']
    r_download = requests.get(url=url_resulting, headers=headers)

    result_raw = r_download.text

    result_parsed = result_raw.replace('/', ',')
    result_parsed = result_parsed.replace('-', ',')

    result_parsed = re.sub('\s+', '', result_parsed)

    result_list = []
    result_list = result_parsed.split(',')

    return result_list
    #filename = studentGitHubAccount + "_" + assignmentID + ".csv"

    #file = open(filename, 'w',)
    #file.write('Assignment_ID,Student_ID,Points_awarded,Points_available,Submission_timestamp' + '\n' +
    #           result_parsed)

    #return r_github.json()


def getStudentsEmail(gitHubUserNames):
    url_github = "https://api.github.com/users/" + gitHubUserNames
    headers = {'Accept': 'application/vnd.github+json','Authorization': 'Bearer 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'}
    try:
        r_github = requests.get(url=url_github, headers=headers)
        studentEmail = r_github.json()['email']

        if(studentEmail == None):
            studentEmail = "Schüler E-Mail nicht öffentlich"

    except:
        studentEmail = 'GitHub Account existiert nicht'
    
    finally:
        return studentEmail

#getAllGitHubStudentsEmails("test")