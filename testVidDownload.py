from deta import Deta
import yt_dlp
import json
import os

# Initialize with a Project Key from DetaBaseKey.txt
with open("DetaBaseKey.txt") as f:
    key = f.read()

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

deta = Deta(key)
db = deta.Base("bricoheroes-base")
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