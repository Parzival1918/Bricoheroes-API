import json

#Read the data from the original file

with open("dataJSON/videoInfo.json") as file:
    fileContents = file.read()

ogData = json.loads(fileContents)

extraVidsCount = 1
for videoData in ogData["videoData"]:
    season = videoData["season"]
    episode = videoData["episode"]

    if season == 0:
        episode = extraVidsCount
        extraVidsCount += 1

    filename = f's{season}e{episode}.json'

    #Save data to new file
    with open(f"dataJSON/parsedData/{filename}", 'w') as file:
        json.dump(videoData, file, indent=0, ensure_ascii=False)
        print(f"Saved s{season} e{episode} to {filename}")