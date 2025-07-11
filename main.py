import curses
from curses.textpad import rectangle
import curses.textpad
import subprocess
import logging
import time
import yt_dlp

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
player = None
ydl_opts = {
    'quiet': True,
    'format': 'bestaudio/best',
    'noplaylist': True,
    'extract_flat': True,
    'force_generic_extractor': False,
    }
current_song = ""

def search(quary, platform: int):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logging.critical(platform)
        match platform:
            case 0:
                info = ydl.extract_info(f"ytsearch5:{quary}", download=False)
            case 1:
                info = ydl.extract_info(f"scsearch5:{quary}", download=False)
            case _:
                logging.critical('idiot')
    result = {}
    
    for video in info.get("entries"):
        result.update({str(video.get("title")): str(video['url'])})
    return result

def stream_audio(url): 
    #function partially by ai, at least for now
    global player

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        global current_song
        current_song = info.get("title")

    player = subprocess.Popen(
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', info['url']],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def main(stdscr: curses.window):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)
    stdscr.bkgd(" ", curses.color_pair(1))

    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    rows, columns = stdscr.getmaxyx()
    rows -=1
    columns -= 1 
    logging.debug(f"rows: {rows}")
    logging.debug(f"Columns: {columns}")
    if rows < 13: #arbitary number: fix later when known
        stdscr.addstr(0, 0, "Terminal is too small!")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        exit()
    
    spaces = int((rows-5)/7)
    logging.critical(spaces)

    typing_win = curses.newwin(spaces, columns-1, 1, 1)
    content_win = curses.newwin(spaces*6, columns-1, int(spaces*2)+3, 1)
    input_box = ""
    selected_row = 0
    choices = {}
    content_size = spaces * 4
    mode = 1
    cursor_position = (1, 1)

    while True:
        rectangle(stdscr, 0, 0, int(spaces)+1, columns)
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, int((columns)/4))
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, int((columns)/4*2))
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, int((columns)/4*3))
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, columns)
        rectangle(stdscr, int(spaces*2)+2, 0 , int(spaces*6)+3, columns)
        rectangle(stdscr, int(spaces*6)+3, 0, int(spaces*7)+4, columns)

        key = stdscr.getch()

        if key == curses.KEY_UP and selected_row != 0:
            selected_row -= 1
        elif key == curses.KEY_DOWN and selected_row != len(choices)+1:
            selected_row += 1

        if selected_row == 0:
            curses.curs_set(1)
            if key == curses.KEY_BACKSPACE:
                input_box = input_box[:-1]
            elif key in (10, 13, curses.KEY_ENTER):
                logging.debug(input_box)
                choices = search(input_box, 0)
            elif 32 <= key <= 126:
                char = chr(key)
                input_box = input_box + str(char)
            cursor_position = (1, len(input_box)+1)
        elif selected_row == 1:
            curses.curs_set(0)
            if key == curses.KEY_LEFT and mode != 1:
                mode -= 1
            if key == curses.KEY_RIGHT and mode != 4:
                mode += 1
        else:
            curses.curs_set(0)
            if key == 10 or key == 13:
                if player != None and player.poll() is None:
                    player.terminate()
                logging.debug(list(choices.values())[selected_row-2])
                stream_audio(list(choices.values())[selected_row-2])

        for i, row in enumerate(list(choices.keys())[:content_size]):
            if i+2 == selected_row:
                content_win.addstr(i, 0, row, curses.color_pair(2))
            else:
                content_win.addstr(i, 0, row, curses.color_pair(1))

        stdscr.addstr(int(spaces*6)+4, 1, f"Now Playing: {current_song}", curses.color_pair(3))
        stdscr.addstr(int(spaces)+2, 1, "SEARCH", curses.color_pair(1))
        stdscr.addstr(int(spaces)+2, int((columns)/4)+1, "ADDED SONGS", curses.color_pair(1))
        stdscr.addstr(int(spaces)+2, int((columns)/4*2)+1, "PLAYLISTS", curses.color_pair(1))
        stdscr.addstr(int(spaces)+2, int((columns)/4*3)+1, "TBC", curses.color_pair(1))

        match mode:
            case 1:
                stdscr.addstr(int(spaces)+2, 1, "SEARCH", curses.color_pair(4))
            case 2:
                stdscr.addstr(int(spaces)+2, int((columns)/4)+1, "ADDED SONGS", curses.color_pair(4))
            case 3:
                stdscr.addstr(int(spaces)+2, int((columns)/4*2)+1, "PLAYLISTS", curses.color_pair(4))
            case 4:
                stdscr.addstr(int(spaces)+2, int((columns)/4*3)+1, "TBC", curses.color_pair(4))

        typing_win.addstr(0, 0, input_box)
        stdscr.move(cursor_position[0], cursor_position[1])

        typing_win.refresh()
        content_win.refresh()
        stdscr.refresh()
        time.sleep(0.03)

if __name__ == "__main__":
    curses.wrapper(main)