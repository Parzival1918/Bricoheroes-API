from fastapi import FastAPI, HTTPException

from typing import Union

import json
from pathlib import Path
from random import choice

tags_metadata = [
    {
        "name": "Informació episodis",
        "description": "Obté informació d'un episodi de la sèrie.",
    },
]

description = """
Obté informació dels capítols de Bricoheroes de Youtube.
"""

app = FastAPI(
    title="bricoheroes-api",
    description=description,
    version="0.1.0",
    contact={
        "name": "Pedro Juan Royo",
        "url": "https://github.com/Parzival1918",
        "email": "pedro.juan.royo@gmail.com",
    },
    # openapi_tags=tags_metadata,
    docs_url="/",
    redoc_url="/alt-docs",
)

@app.get("/info-episodi/{temporada}/{episodi}", tags=["Informació episodis"], description="Obté l'informació d'un episodi.")
def informacio_episodi(temporada: int, episodi: int):
    filename = f"s{temporada}e{episodi}.json"
    filepath = Path(f"dataJSON/parsedData/{filename}")
    #Check that file exists
    if filepath.is_file():
        with open(filepath) as file:
            fileContents = json.load(file)
    else:
        raise HTTPException(status_code=400, detail="L'episodi d'aquesta temporada no existeix")

    return fileContents

@app.get("/episodi-aleatori", tags=["Informació episodis"], description="Obté l'informació d'un episodi aleatori de la sèrie.")
def episodi_aleatori(inclou_extres: Union[bool, None] = False):
    #Get a random file from the folder
    filepath = Path("dataJSON/parsedData/")
    files = [f for f in filepath.iterdir() if f.is_file()]
    if not inclou_extres:
        files = [f for f in files if (not f.stem.startswith("s0"))]

    randomFile = choice(files)
    with open(randomFile) as file:
        fileContents = json.load(file)

    return fileContents

@app.get("/episodis-temporada/{temporada}", tags=["Informació episodis"], description="Obté tots els episodis d'una temporada.")
def episodis_temporada(temporada: int):
    filepath = Path("dataJSON/parsedData/")
    files = [f for f in filepath.iterdir() if f.is_file()]
    files = [f for f in files if (f.stem.startswith(f"s{temporada}"))]
    if len(files) == 0:
        raise HTTPException(status_code=401, detail="Temporada no existeix")

    files = sorted(files, key=lambda f: int(f.stem.removeprefix(f"s{temporada}e"))) #Sort in ascending order

    fileContents = []
    for file in files:
        with open(file) as f:
            fileContents.append(json.load(f))

    return fileContents

def search_word(word: str, text: str):
    for w in text.split(sep=" "):
        if word == w: #Exact match
            print(f"Exact matching {w} |-| {word}")
            return True
        if (word in w or w in word) and abs(len(word)-len(w)) <= 2 and len(w) > 2:
            print(f"Matching {w} |-| {word}")
            return True

@app.get("/busca-episodi/{cerca}", tags=["Informació episodis"], description="Busca un episodi a partir d'una paraula clau.")
def busca_epsiodi(cerca: str, cerca_descripcio: Union[bool, None] = False):
    #Get the episode data
    filepath = Path("dataJSON/parsedData/")
    files = [f for f in filepath.iterdir() if f.is_file()]
    fileContents = []
    for file in files:
        with open(file) as f:
            fileContents.append(json.load(f))

    matchingEps = []
    for episode in fileContents:
        # if episode["videoTitle"].lower().find(cerca.lower()) != -1:
        #     matchingEps.append(episode)
        # elif cerca_descripcio and episode["videoDescription"].lower().find(cerca.lower()) != -1:
        #     matchingEps.append(episode)
        if search_word(cerca.lower(), episode["videoTitle"].lower()):
            matchingEps.append(episode)
        elif cerca_descripcio:
            if search_word(cerca.lower(), episode["videoDescription"].lower()):
                matchingEps.append(episode)

    return matchingEps

@app.get("/test-DetaBase", tags=["Informació episodis"], description="Test de la base de dades.")
def test_DetaBase():
    from deta import Deta
    from pathlib import Path
    
    # Initialize with a Project Key from DetaBaseKey.txt
    with open("DetaBaseKey.txt") as f:
        key = f.read()
    
    deta = Deta(key)
    db = deta.Base("bricoheroes-base")
    
    # Read from the database
    data = db.get("s1e1")
    data["value"] = json.loads(data["value"])
    
    return data