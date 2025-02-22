#!/usr/bin/python3

import os
import time
import curses
from tabulate import tabulate

#Cache the directory size

dir_cache={}

tabulate.PRESERVE_WHITESPACE = True

COLOR_TABLE = 1
COLOR_HIGHLIGHT = 2

#To convert the the size from byte to KB, MB etc..
def format_size(size_in_bytes):

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def get_folder_size(path):
    if path in dir_cache:
        return dir_cache[path]

    total_size = 0
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_symlink():
                    continue
                if entry.is_file(follow_symlinks=False):
                    total_size += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    total_size += get_folder_size(entry.path)
    except PermissionError:
        pass 
    dir_cache[path]=total_size
    return total_size


def gather_directory_data(directory, sort):
    sort_key = 0 if sort is None else 1
    data = []

    for entry in os.listdir(directory):
        if entry.startswith('.'):
            continue
        
        entry_path = os.path.join(directory, entry)
        entry_name = f"/{entry}" if os.path.isdir(entry_path) else entry
        entry_size = get_folder_size(entry_path) if os.path.isdir(entry_path) else os.path.getsize(entry_path)
        entry_date = time.ctime(os.path.getmtime(entry_path))

        data.append([entry_name, entry_size, entry_date])  

    data.sort(key=lambda x: x[sort_key])

    for item in data:
        item[1] = format_size(item[1])  

    return data


def generate_headers(directory, terminal_width):

    col_widths = [max(int(terminal_width * 0.50), 10),
                  max(int(terminal_width * 0.20), 10),
                  max(int(terminal_width * 0.20), 10)]
    return [
        f"{directory:<{col_widths[0]}}",
        f"{'Size':<{col_widths[1]}}",
        f"{'Last date modified':<{col_widths[2]}}"
    ]

def handle_key_input(key, cursor_row, directory, data):
    max_cursor = 3 + (len(data) * 2)

    if key == curses.KEY_UP and cursor_row > 3:
        return cursor_row - 2, directory,None  # Move up
    elif key == curses.KEY_DOWN and cursor_row < max_cursor - 2:
        return cursor_row + 2, directory, None  # Move down
    elif key == ord('q'):
        return None, None, None
    elif key== ord('s'):
        return cursor_row, directory, "size"
    elif key == curses.KEY_LEFT:
        return 3, os.path.dirname(directory) ,None # Move back
    elif key == 10:  # Enter key
        data_index = (cursor_row - 3) // 2
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))

            if os.path.isdir(selected_path):
                return 3, selected_path  # Navigate into folder
            else:
                os.system(f"xdg-open '{selected_path}'")
                return cursor_row, directory  # Stay in the same directory
    return cursor_row, directory , None # Default case (no change)

def main(stdscr):
    curses.start_color()
    curses.init_pair(COLOR_TABLE, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    sort=None
    current_path = os.getcwd()
    cursor_row = 3

    while True:
        stdscr.clear()
        terminal_width = stdscr.getmaxyx()[1]
        directory_data = gather_directory_data(current_path, sort)
        headers = generate_headers(current_path, terminal_width)
        rows = tabulate(directory_data, headers=headers, tablefmt="grid", maxcolwidths=[None, 18]).splitlines()

        for i, row in enumerate(rows):
            truncated_row = row[:terminal_width - 1]
            if i == cursor_row:
                stdscr.addstr(f"{truncated_row}\n", curses.color_pair(COLOR_HIGHLIGHT) | curses.A_REVERSE)
            else:
                stdscr.addstr(f"{truncated_row}\n", curses.color_pair(COLOR_TABLE))
        
        stdscr.refresh()
        key = stdscr.getch()
        
        new_cursor, new_path, sort_struck = handle_key_input(key, cursor_row, current_path, directory_data)
        if new_cursor is None:
            break 

        cursor_row, current_path, sort = new_cursor, new_path, sort_struck
        
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
