#!/usr/bin/python3

import os
import time
from tabulate import tabulate
import curses

tabulate.PRESERVE_WHITESPACE = True

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024


def sizeofFolder(path):
    folderSize = 0
    listItems = os.listdir(path)
    for j in listItems:
        itemPath = os.path.join(path, j)
        if os.path.islink(itemPath):
            continue
        if os.path.isfile(itemPath):
            folderSize += os.path.getsize(itemPath)
        else:
            folderSize += sizeofFolder(itemPath)
    return folderSize

def fill_data_for_tabulate(current_dir):
    dirs = os.listdir(current_dir)
    
    data = []
#hello;
    for i in dirs:
        if i.startswith('.'):
            continue
        path = os.path.join(current_dir, i)
    
        if os.path.isfile(path):
            fileName = os.path.basename(path)
            fileSize = os.path.getsize(path)
            sizeName = format_size(fileSize)
            fileDate = time.ctime(os.path.getmtime(path))
            data.append([fileName, sizeName, fileDate])
        else:  
            fileName = f"/{os.path.basename(path)}"
            folderSize = sizeofFolder(path)
            sizeName = format_size(folderSize)
            fileDate = time.ctime(os.path.getmtime(path))
            data.append([fileName, sizeName, fileDate])
    return data


def main(stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    
    path = f"{os.getcwd()}"
    current_dir = f"{path}"

    data = fill_data_for_tabulate(current_dir)
    terminal_width = stdscr.getmaxyx()[1]
    col_widths = [max(int(terminal_width * 0.4), 10), max(int(terminal_width * 0.25), 10), max(int(terminal_width * 0.25), 10)]
    headers = [
                f"{os.getcwd():<{col_widths[0]}}",
                f"{'Size':<{col_widths[1]}}",
                f"{'Date of Creation':<{col_widths[2]}}"
            ]
        
        
    rows = tabulate(data, headers=headers, tablefmt="heavy_grid", maxcolwidths=[None, 18]).splitlines()
    
    cursor_row = 3
    
    while True:
        stdscr.clear()
        
        current_dir = f"{path}"
        data = fill_data_for_tabulate(current_dir)
        
        terminal_width = stdscr.getmaxyx()[1]
        col_widths = [max(int(terminal_width * 0.4), 10), max(int(terminal_width * 0.25), 10), max(int(terminal_width * 0.25), 10)]
        headers = [
                    f"{os.getcwd():<{col_widths[0]}}",
                    f"{'Size':<{col_widths[1]}}",
                    f"{'Date of Creation':<{col_widths[2]}}"
                ]
        
        
        rows = tabulate(data, headers=headers, tablefmt="heavy_grid", maxcolwidths=[None, 18]).splitlines()

        for i, row in enumerate(rows):
            # Truncate the row to fit the terminal width
            truncated_row = row[:terminal_width - 1]
            if i == cursor_row:
                stdscr.addstr(f"{truncated_row}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"{truncated_row}\n")

        
        stdscr.refresh()
        key = stdscr.getch()
        
        if key == curses.KEY_UP and cursor_row > 3:
            cursor_row -= 2
        elif key == curses.KEY_DOWN and cursor_row < len(rows) - 2:
            cursor_row += 2
        elif key == ord('q'):
            break
        elif key==curses.KEY_LEFT:
            path=os.path.dirname(current_dir)
        elif key == 10:  
            data_index = (cursor_row - 3) // 2  
            if 0 <= data_index < len(data):  
                selected_entry = data[data_index][0]

                if selected_entry.startswith("/"):
                    path = os.path.join(current_dir, selected_entry.lstrip('/'))

                    data = fill_data_for_tabulate(path)
                    terminal_width = stdscr.getmaxyx()[1]
                    col_widths = [max(int(terminal_width * 0.4), 10), max(int(terminal_width * 0.25), 10), max(int(terminal_width * 0.25), 10)]
                    headers = [
                        f"{os.getcwd():<{col_widths[0]}}",
                        f"{'Size':<{col_widths[1]}}",
                        f"{'Date of Creation':<{col_widths[2]}}"
                    ]
                    rows = tabulate(data, headers=headers, tablefmt="heavy_grid", maxcolwidths=[None, 18]).splitlines()
                    cursor_row = 3
                    
                else:
                    os.system(f"xdg-open '{path}'")
    
    curses.endwin()

        

if  __name__ == "__main__":
    curses.wrapper(main)