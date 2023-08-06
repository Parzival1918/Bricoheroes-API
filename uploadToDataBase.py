from deta import Deta
from pathlib import Path

# Initialize with a Project Key from DetaBaseKey.txt
with open("DetaBaseKey.txt") as f:
    key = f.read()

deta = Deta(key)
db = deta.Base("bricoheroes-base")

# Upload all files from dataJSON/parsedData to the database
filepath = Path("dataJSON/parsedData/")
files = [f for f in filepath.iterdir() if f.is_file()]

dbStructure = {}
for file in files:
    with open(file) as f:
        fileContents = f.read()
    # print(fileContents)
    # print()
    # db.put(fileContents, file.stem)
    print(f"Uploaded {file.stem} to the database")

    #Get season and episode
    season = int(file.stem.split("e")[0][1:])
    episode = int(file.stem.split("e")[1])

    seasonTxt = f"Temporada {season}"

    #Check if the season exists in dbStructure
    if seasonTxt not in dbStructure:
        dbStructure[seasonTxt] = 0

    dbStructure[seasonTxt] += 1

print(dbStructure)
db.put(dbStructure, "continguts")