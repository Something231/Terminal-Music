import curses
import yt_dlp
import subprocess
import logging
import time

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
player = None
ydl_opts = {
    'quiet': True,
    'format': 'bestaudio/best',
    'noplaylist': True,
    'extract_flat': True,
    'force_generic_extractor': False,
    }

def yt_search(quary):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{quary}", download=False)
    for video in info.get("entries"):
        logging.debug(str(video.get("title"))+f"https://www.youtube.com/watch?v={video['id']}")

def stream_youtube(url): 
    #function partially by ai, at least for now
    global player

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    player = subprocess.Popen(
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', info['url']],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def main(stdscr: curses.window):
    curses.start_color()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)

    stdscr.nodelay(True)
    stdscr.keypad(True)

    selectedrow = 0
    choices = {"rick": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "other": "https://www.youtube.com/watch?v=XkFz_hi2tWY"}

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Choose something to play below:")

        for i, row in enumerate(choices.keys()):
            if i == selectedrow:
                stdscr.addstr(i+1, 0, row, curses.color_pair(2))
            else:
                stdscr.addstr(i+1, 0, row, curses.color_pair(1))

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selectedrow != 0:
            selectedrow -= 1
        elif key == curses.KEY_DOWN and selectedrow != len(choices)-1:
            selectedrow += 1
        elif key == 10 or key == 13:
            if player != None and player.poll() is None:
                player.terminate()
            logging.debug(list(choices.values())[selectedrow])
            stream_youtube(list(choices.values())[selectedrow])
        
        time.sleep(0.03)

if __name__ == "__main__":
    curses.wrapper(main)