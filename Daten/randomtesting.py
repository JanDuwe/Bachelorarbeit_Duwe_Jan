from generate_sampledata import * 
import pandas as pd



assignments = generateAssignments()
print(assignments)

students = generateRandomStudents()
print(students)
print(type(students))

gradings = generateRandomGradings(students, assignments)
pd.set_option('display.max_rows', gradings.shape[0]+1)

print(gradings)



