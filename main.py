#!/usr/bin/python3
import curses
import os
import tabulate
import file_utils as file
import input_handler as input
import config

tabulate.PRESERVE_WHITESPACE = True

def main(stdscr):
   
    curses.start_color()
    curses.init_pair(config.COLOR_TABLE, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(config.COLOR_HIGHLIGHT, curses.COLOR_WHITE, curses.COLOR_BLUE)
   
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    sort='a'
    sort_def=sort
    
    current_path = os.getcwd()
    
    cursor_row = 3
    
    terminal_width = stdscr.getmaxyx()[1]
    
    while True:
    
        stdscr.clear()
    
        directory_data = file.gather_directory_data(current_path, sort)
        headers = file.generate_headers(current_path, terminal_width)
        rows = tabulate.tabulate(directory_data, headers=headers, tablefmt="grid", maxcolwidths=[None, 18]).splitlines()
        
        for i, row in enumerate(rows):
           
            truncated_row = row[:terminal_width - 1]
           
            if i == cursor_row:
                stdscr.addstr(f"{truncated_row}\n", curses.color_pair(config.COLOR_HIGHLIGHT) | curses.A_REVERSE)
           
            else:
                stdscr.addstr(f"{truncated_row}\n", curses.color_pair(config.COLOR_TABLE))
        
        stdscr.refresh()
        key = stdscr.getch()
        sort_struck=sort_def
        
        new_cursor, new_path, sort_struck= input.handle_key_input(key, cursor_row, current_path, directory_data, sort_def)
        if new_cursor is None:
            break 

        cursor_row, current_path, sort = new_cursor, new_path, sort_struck
        sort_def=sort
        
    curses.endwin()


if __name__ == "__main__":
    import curses
    curses.wrapper(main)