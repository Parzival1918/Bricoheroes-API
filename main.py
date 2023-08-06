from fastapi import FastAPI, HTTPException

from typing import Union

import json
from pathlib import Path
from random import choice
from deta import Deta

# Initialize with a Project Key from DetaBaseKey.txt
with open("DetaBaseKey.txt") as f:
    key = f.read()
    
deta = Deta(key)
db = deta.Base("bricoheroes-base")

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
    # Create the key
    key = f"s{temporada}e{episodi}"

    # Read from the database
    data = db.get(key)
    if data is None:
        raise HTTPException(status_code=401, detail="Episodi no existeix")

    data["value"] = json.loads(data["value"])    

    return data

@app.get("/episodi-aleatori", tags=["Informació episodis"], description="Obté l'informació d'un episodi aleatori de la sèrie.")
def episodi_aleatori(inclou_extres: Union[bool, None] = False):
    # Get the episode data from continguts in the database
    continguts = db.get("continguts")

    #Get a random season
    keys = list(continguts.keys())
    keys.remove("key") #remove continguts key
    if not inclou_extres:
        keys.remove("Temporada 0") #remove Extres key
    print(keys)

    temporada = choice(keys)
    print(temporada)

    #Get a random episode
    episodi = choice(range(1, continguts[temporada]+1))
    print(f"Episodi: {episodi}")

    #Get the episode data
    temporada = temporada.replace("Temporada ", "")
    key = f"s{temporada}e{episodi}"
    data = db.get(key)
    data["value"] = json.loads(data["value"])

    return data

@app.get("/episodis-temporada/{temporada}", tags=["Informació episodis"], description="Obté tots els episodis d'una temporada.")
def episodis_temporada(temporada: int):
    #Get the amount of episodes in the season
    continguts = db.get("continguts")
    try:
        numEpisodes = continguts[f"Temporada {temporada}"]
    except KeyError:
        raise HTTPException(status_code=402, detail="Temporada no existeix")

    #Get the episode data
    episodeContents = []
    for episode in range(1, numEpisodes+1):
        key = f"s{temporada}e{episode}"
        data = db.get(key)
        data["value"] = json.loads(data["value"])
        episodeContents.append(data)

    return episodeContents

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
    #Get the episode data from continguts in the database
    continguts = db.get("continguts")
    keys = list(continguts.keys())
    keys.remove("key") #remove continguts key

    matchingEps = []
    for temporada in keys:
        #Get the amount of episodes in the season
        numEpisodes = continguts[temporada]

        print(f"Searching in {temporada} with {numEpisodes} episodes")
        temporada = temporada.replace("Temporada ", "")
        #Get the episode data
        for episode in range(1, numEpisodes+1):
            key = f"s{temporada}e{episode}"
            data = db.get(key)
            data["value"] = json.loads(data["value"])
            if search_word(cerca, data["value"]["videoTitle"].lower()):
                matchingEps.append(data)
            elif cerca_descripcio:
                if search_word(cerca, data["value"]["videoDescription"].lower()):
                    matchingEps.append(data)

    return matchingEps