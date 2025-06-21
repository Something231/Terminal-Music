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
    result = {}
    for video in info.get("entries"):
        result.update({str(video.get("title")): f"https://www.youtube.com/watch?v={str(video['id'])}"})
    return result

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
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)

    stdscr.nodelay(True)
    stdscr.keypad(True)

    inputbox = ""
    selectedrow = 0
    choices = {}

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Type and press enter to search below:", curses.A_BOLD)

        for i, row in enumerate(choices.keys()):
            if i+1 == selectedrow:
                stdscr.addstr(i+2, 0, row, curses.color_pair(2))
            else:
                stdscr.addstr(i+2, 0, row, curses.color_pair(1))

        key = stdscr.getch()
        if key == curses.KEY_UP and selectedrow != 0:
            selectedrow -= 1
        elif key == curses.KEY_DOWN and selectedrow != len(choices):
            selectedrow += 1

        if selectedrow == 0:
            curses.curs_set(1)
            if key == curses.KEY_BACKSPACE:
                inputbox = inputbox[:-1]
            elif key in (10, 13, curses.KEY_ENTER):
                logging.debug(inputbox)
                choices = yt_search(inputbox)
            elif 32 <= key <= 126:
                char = chr(key)
                inputbox = inputbox + str(char)
            stdscr.move(1, len(inputbox)+1)

        else:
            curses.curs_set(0)
            if key == 10 or key == 13:
                if player != None and player.poll() is None:
                    player.terminate()
                logging.debug(list(choices.values())[selectedrow-1])
                stream_youtube(list(choices.values())[selectedrow-1])
        
        stdscr.addstr(1, 0, inputbox)
        stdscr.refresh()
        time.sleep(0.03)

if __name__ == "__main__":
    curses.wrapper(main)