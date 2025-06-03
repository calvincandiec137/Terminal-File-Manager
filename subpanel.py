import curses
import time
import os
import main as m
import file_utils as file
import subprocess

def git(subpanel, focused):
   result = subprocess.run(['git',  'status'], stdout=subprocess.PIPE, cwd = focused.path)
   lines = result.stdout.splitlines()
   
   subpanel.addstr(0, 2, "Git status", curses.color_pair(m.COLOR_TABLE))
   
   for i, line in enumerate(lines):
       subpanel.addstr(i+1, 1, line, curses.color_pair(m.COLOR_TABLE))
   
   subpanel.refresh()
    
def text_lines(subpanel, focused):
    lines = []

    file_panel = focused.data[focused.cursor_row - 3][0].lstrip('/')
    file_path = os.path.join(focused.path, file_panel)
    
    with open(file_path, 'r') as f:
        for _, line in zip(range(30), f):
            lines.append(line.rstrip('\n'))

    for i in range(min(25, len(lines))):
        subpanel.addstr(i+1, 1, lines[i][:83], curses.color_pair(m.COLOR_TABLE))
    subpanel.addstr(0, 2, f"{os.path.basename(file_path)}", curses.color_pair(m.COLOR_TABLE))
    
    subpanel.refresh()

def dir_info(subpanel, focused):
    
    files_count = 0
    dirs_count = 0
    
    try:
        for entry in os.listdir(focused.path):
            full_path = os.path.join(focused.path, entry)
            if os.path.isfile(full_path):
                files_count += 1
            elif os.path.isdir(full_path):
                dirs_count += 1
    except Exception:
        files_count = 0
        dirs_count = 0
    subpanel.addstr(0, 2, "Directory Info", curses.color_pair(m.COLOR_TABLE))
    subpanel.addstr(1, 1, f"Name: {focused.path}",curses.color_pair( m.COLOR_TABLE))
    subpanel.addstr(2, 1, f"Size: {round(file.get_folder_size(focused.path)/1024, 2)} KB", curses.color_pair( m.COLOR_TABLE))
    subpanel.addstr(3, 1, f"Files: {files_count}", curses.color_pair(m.COLOR_TABLE))
    subpanel.addstr(4, 1, f"Dirs: {dirs_count}", curses.color_pair(m.COLOR_TABLE))
    
    subpanel.refresh()
    
    