from fileinput import filename
import requests
import csv
import re

"""Falls die Funktionalität überprüft werden soll, müssen hier in den beiden Funktionen bei den Headers das GitHub API Token für 'token' eingesetzt werden."""

def getAssignmentResults(studentGitHubAccount, assignment_name):
    """Implementiert die REST Anfrage an ein GitHub Repository um das Ergebnis eines Schülers zu exportieren."""

    url_github = "https://api.github.com/repos/JanDuweBachelorarbeit/" + assignment_name + "-" + studentGitHubAccount + "/contents/metadata_raw.csv"
    headers = {'Accept': 'application/vnd.github+json','Authorization': 'Bearer token'}
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

def getStudentsEmail(gitHubUserNames):
    """Implementiert die REST Anfrage an ein GitHub Nutzerkonto um die hinterlegte, öffentlich sichtbare E-Mail abzufragen."""
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