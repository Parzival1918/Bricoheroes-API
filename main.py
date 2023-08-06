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
Obté informació dels capítols de Bricoheroes a Youtube.
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

@app.get("/info-episodi/{temporada}/{episodi}", tags=["Informació episodis"])
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

@app.get("/episodi-aleatori", tags=["Informació episodis"])
def episodi_aleatori(inclou_extres: Union[bool, None] = False):
    #Get a random file from the folder
    filepath = Path("dataJSON/parsedData/")
    files = [f for f in filepath.iterdir() if f.is_file()]
    if not inclou_extres:
        files = [f for f in files if (not f.stem[0].startswith("s0"))]

    randomFile = choice(files)
    with open(randomFile) as file:
        fileContents = json.load(file)

    return fileContents