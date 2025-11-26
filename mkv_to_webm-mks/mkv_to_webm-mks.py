from glob import glob
from threading import Thread
from os import system as cmd
from os import remove,sep
from os.path import abspath
from os import makedirs

jobs = []

def launch_job(command):
    jobs.append( Thread(target=cmd, args=(command,)) ) 

def mkv2webm(file):
    new_filename = ".".join(file[::-1].split(".")[1:])[::-1]+".webm"
    return f'ffmpeg -i "{file}" -map 0:v:0 -map 0:a:0 -map_metadata 0 -map_chapters 0 -c copy -c:a opus -strict -2 "{new_filename}"'

def extsubs(file):
    new_filename = ".".join(file[::-1].split(".")[1:])[::-1]+".mks"
    return f'ffmpeg -i "{file}" -map 0:s -map_metadata 0 -map_chapters -1 -c copy -f matroska "{new_filename}"'

def extthumb(file):
    makedirs(".thumbnails", exist_ok=True)
    new_filename = ".".join(file[::-1].split(".")[1:])[::-1]+".webp"
    new_filename = ".thumbnails"+sep+new_filename
    return f'ffmpeg -ss 30 -i "{file}" -frames:v 1 -vf "scale=1280:720" "{new_filename}"'

def remove_name(file):
    return f'mkvpropedit "{file}" -e info -d title'


def main():
    files = glob("*.mkv")

    for x in files:
        launch_job( remove_name(x) )

    for x in jobs: x.start()
    for x in jobs: x.join()
    jobs.clear()

    for x in files:
        launch_job( mkv2webm(x) )
        launch_job( extsubs(x)  )
        launch_job( extthumb(x) )

    for x in jobs: x.start()
    for x in jobs: x.join()

    for x in files: remove(x)

    remove(abspath(__file__))


if __name__ == "__main__": main()

