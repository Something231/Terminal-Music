import curses
from curses.textpad import rectangle
import curses.textpad
import subprocess
import logging
import time
logging.basicConfig(filename="debug.log", level=logging.DEBUG)


def main(stdscr: curses.window):
    curses.start_color()
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    rows, columns = stdscr.getmaxyx()
    rows -=1
    columns -= 1 
    logging.debug(f"rows: {rows}")
    logging.debug(f"Columns: {columns}")
    if rows < 12: #arbitary number: fix later when known
        stdscr.addstr(0, 0, "Terminal is too small!")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        exit()
    
    #typing_win = curses.newwin()
    #content_box = curses.newwin()
    #curr_box = curses.newwin()
    spaces = int((rows-5)/7)
    logging.critical(spaces)
    while True:
        rectangle(stdscr, 0, 0, int(spaces)+1, columns)
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, int((columns)/4))
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, int((columns)/4*2))
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, int((columns)/4*3))
        rectangle(stdscr, int(spaces)+1, 0, int(spaces*2)+2, columns)
        rectangle(stdscr, int(spaces*2)+2, 0 , int(spaces*6)+3, columns)
        rectangle(stdscr, int(spaces*6)+3, 0, int(spaces*7)+4, columns)

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)