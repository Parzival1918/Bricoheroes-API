from fastapi import FastAPI, HTTPException

from typing import Union

import json
from random import choice
from deta import Deta
from pydantic import BaseModel
import yt_dlp
import os

# Initialize with a Project Key from DetaBaseKey.txt
with open("DetaBaseKey.txt") as f:
    key = f.read()
    
deta = Deta(key)
db = deta.Base("bricoheroes-base")

tags_metadata = [
    {
        "name": "Informació episodi",
        "description": "Obté informació d'un episodi de la sèrie.",
    },
    {
        "name": "Informació episodis",
        "description": "Obté informació de multiples episodis de la sèrie.",
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

class VideoDescription(BaseModel):
    height: int
    url: str
    width: int

class VideoTumbnails(BaseModel):
    default: VideoDescription
    medium: VideoDescription
    high: VideoDescription
    standard: VideoDescription
    maxres: VideoDescription

class InfoEpisodi(BaseModel):
    videoId: str
    videoTitle: str
    videoDescription: str
    videoThumbnails: VideoTumbnails
    videoDate: str
    videoLink: str
    season: int
    episode: int

@app.get("/info-episodi/{temporada}/{episodi}", tags=["Informació episodi"], description="Obté l'informació d'un episodi.", response_model=InfoEpisodi)
def informacio_episodi(temporada: int, episodi: int):
    # Create the key
    key = f"s{temporada}e{episodi}"

    # Read from the database
    data = db.get(key)
    if data is None:
        raise HTTPException(status_code=401, detail="Episodi no existeix")

    data["value"] = json.loads(data["value"])    

    return data["value"]

@app.get("/info-episodi/aleatori", tags=["Informació episodi"], description="Obté l'informació d'un episodi aleatori de la sèrie.", response_model=InfoEpisodi)
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

    return data["value"]

class InfoEpisodis(BaseModel):
    episodis: list[InfoEpisodi]

@app.get("/info-episodis/temporada/{temporada}", tags=["Informació episodis"], description="Obté tots els episodis d'una temporada.", response_model=InfoEpisodis)
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
        episodeContents.append(data["value"])

    return {"episodis": episodeContents}

def search_word(word: str, text: str):
    for w in text.split(sep=" "):
        if word == w: #Exact match
            print(f"Exact matching {w} |-| {word}")
            return True
        if (word in w or w in word) and abs(len(word)-len(w)) <= 2 and len(w) > 2:
            print(f"Matching {w} |-| {word}")
            return True
        
    return False

@app.get("/info-episodis/cerca/{cerca}", tags=["Informació episodis"], description="Busca un episodi a partir d'una paraula clau.", response_model=InfoEpisodis)
def busca_epsiodi(cerca: str, cerca_descripcio: bool = False):
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
                matchingEps.append(data["value"])
            elif cerca_descripcio:
                if search_word(cerca, data["value"]["videoDescription"].lower()):
                    matchingEps.append(data["value"])

    return {"episodis": matchingEps}

#Deta Space actions

def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1] # reverse
    # print(ctx.get('formats'))
    # print(formats)

    for f in formats:
        try:
            print(f"{f['format_id']} ext: {f['ext']} vcodec: {f['vcodec']} acodec: {f['acodec']} quality: {f['quality']} width: {f['width']} height: {f['height']}")
        except:
            pass
        
    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none' and f['ext'] == 'mp4')
    # print(best_video)

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    audio_ext = {'mp4': 'm4a'}[best_video['ext']]
    print(best_video['ext'])
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

def uploadVideos():
    dd = deta.Drive("bricoheroes-drive")

    res = db.fetch()
    all_items = res.items

    # Continue fetching until "res.last" is None.
    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items

    vidCount = 0
    for item in all_items:
        if item["key"] != "continguts" and "s0" in item["key"]:
            #Check if the video is already downloaded
            dd.get(item["key"])

            if dd.get(f"{item['key']}.mp4") != None:
                print(f"Video: {item['key']} already downloaded")
                continue

            itemConts = json.loads(item["value"])
            vidLink = itemConts["videoLink"]
            filename = item["key"]
            print(vidLink, filename)

            ydl_opts = {
                'format': format_selector,
                'outtmpl': filename,
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vidLink])
                pass
            print(f"Downloaded {filename}")

            # Upload the video to Deta Drive
            filename = filename + ".mp4"
            dd.put(filename, open(filename, "rb"))
            print(f"Uploaded {filename} to Deta Drive")

            # Delete the video from the local storage
            os.remove(filename)

            vidCount += 1

            if vidCount == 5:
                break
    
    print(f"Uploaded {vidCount} videos")

class DetaEvent(BaseModel):
    id: str
    trigger: str

class DetaSpaceActions(BaseModel):
    event: DetaEvent

@app.post("/__space/v0/actions", tags=["Actualitza informació"], description="Actualitza la informació dels episodis del podcast, **no es pot accedir.**", include_in_schema=True)
def actualitza_info(action: DetaSpaceActions):
    action = action.model_dump()
    actionID = action["event"]["id"]

    if actionID == "uploadVideos":
        uploadVideos()
    else:
        raise HTTPException(status_code=403, detail="Action not found")

    return {"message": f"Action {actionID} received"}