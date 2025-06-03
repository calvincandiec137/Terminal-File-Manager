#!/usr/bin/python3
import curses
import os
import tabulate
import file_utils as file
import input_handler as input
import time
import subpanel as sp

COLOR_TABLE = 1
COLOR_HIGHLIGHT = 2

class WindowState:
    def __init__(self, win):
        self.path = os.getcwd()
        self.sort = 'a'
        self.cursor_row = 3
        self.scroll_offset = 0
        self.win = win
        self.focused = False
        self.rows = []
        self.data = []

def render_window(panel, height, width):
    panel.win.clear()
    if not panel.data or not panel.rows:
        panel.data = file.gather_directory_data(panel.path, panel.sort, height)
        headers = file.generate_headers(panel.path, width)
        panel.rows = tabulate.tabulate(panel.data, headers=headers, tablefmt="rounded_outline", maxcolwidths=[None, 18]).splitlines()

    max_displayable_rows = height - 1
    total_rows = len(panel.rows)
    max_scroll = max(0, total_rows - max_displayable_rows)
    panel.scroll_offset = max(0, min(panel.scroll_offset, max_scroll))

    start_row = panel.scroll_offset
    end_row = min(start_row + max_displayable_rows, total_rows)

    for i in range(start_row, end_row):
        row = panel.rows[i][:width - 1]
        try:
            if i == panel.cursor_row and panel.focused:
                panel.win.addstr(i - start_row, 0, row, curses.color_pair(COLOR_HIGHLIGHT) | curses.A_REVERSE)
            else:
                panel.win.addstr(i - start_row, 0, row, curses.color_pair(COLOR_TABLE))
        except curses.error:
            break

def render_side_panel(subpanel, panel_type="tree", focused_panel=None):
    subpanel.clear()
    height, width = subpanel.getmaxyx()

    for i in range(height):
        if i == 0:
            border_str = f"╭{'─' * (width - 3)}╮"
            subpanel.addstr(i, 0, border_str[:width], curses.color_pair(COLOR_TABLE))
        elif i == height - 1:
            border_str = f"╰{'─' * (width - 3)}╯"
            subpanel.addstr(i, 0, border_str[:width], curses.color_pair(COLOR_TABLE))
        else:
            subpanel.addstr(i, 0, "│", curses.color_pair(COLOR_TABLE))
            if width > 1:
                subpanel.addstr(i, width - 2, "│", curses.color_pair(COLOR_TABLE))
                
        if panel_type == "tree":
            
            type_of_element = focused_panel.data[focused_panel.cursor_row - 3][0].lstrip('/')
            element_path = os.path.join(focused_panel.path, type_of_element)
            if type_of_element == ".git":
                sp.git(subpanel,focused_panel)
            elif os.path.isfile(element_path):
                sp.text_lines(subpanel, focused_panel)
            else :
                sp.dir_info(subpanel, focused_panel)
    
    file_panel = focused_panel.data[focused_panel.cursor_row - 3][0].lstrip('/')
    file_path = os.path.join(focused_panel.path, file_panel)
    size = 0
    try: 
        file_stat = os.stat(file_path)
        size = round(file_stat.st_size / (1024), 2)  if os.path.isfile(file_path    ) else  round(file.get_folder_size(file_path)/ (1024), 2)
    except FileNotFoundError:
        pass
    
    try:
        if panel_type == "properties":
            i=1
            subpanel.addstr(0, 2, "File Info", curses.color_pair(COLOR_TABLE))
            subpanel.addstr(i, 1, f'Name: {os.path.basename(file_path)}', curses.color_pair(COLOR_TABLE));
            subpanel.addstr(i, 1, f'Path: {os.path.abspath(file_path)}', curses.color_pair(COLOR_TABLE)); i += 1
            subpanel.addstr(i, 1, f'Size: {size} KB', curses.color_pair(COLOR_TABLE)); i += 1
            subpanel.addstr(i, 1, f'Created: {time.ctime(file_stat.st_ctime)}', curses.color_pair(COLOR_TABLE)); i += 1
            subpanel.addstr(i, 1, f'Modified: {time.ctime(file_stat.st_mtime)}', curses.color_pair(COLOR_TABLE)); i += 1
            subpanel.addstr(i, 1, f'Permissions: {oct(file_stat.st_mode & 0o777)}', curses.color_pair(COLOR_TABLE)); i += 1
    except UnboundLocalError:
        pass

                    
    subpanel.refresh()

def calculate_layout(term_height, term_width):
 
    MIN_SIDE_PANEL_WIDTH = 15
    MIN_HEIGHT = 10
    
    # use minimal if terminal too small
    if term_width < 60 or term_height < 20:
        side_panel_width = max(MIN_SIDE_PANEL_WIDTH, term_width // 6)
        main_width = term_width - side_panel_width
        left_width = main_width // 2
        right_width = main_width - left_width
    else:
        side_panel_width = max(MIN_SIDE_PANEL_WIDTH, min(term_width // 2, 100))
        main_width = term_width - side_panel_width
        left_width = main_width // 2
        right_width = main_width - left_width   
    
    tree_height = max(MIN_HEIGHT // 2, term_height * 3 // 4) - 2 # -2 cuz the right left panel are of not full lenght
    prop_height = term_height - tree_height - 6
    
    return {
        'left_width': left_width,
        'right_width': right_width,
        'side_panel_width': side_panel_width,
        'tree_height': tree_height,
        'prop_height': prop_height,
        'main_width': main_width
    }

def create_win(stdscr, layout):

    term_height, term_width = stdscr.getmaxyx()
    
    try:
        left_win = stdscr.subwin(
            term_height, 
            layout['left_width'], 
            0, 0
        )
        
        right_win = stdscr.subwin(
            term_height, 
            layout['right_width'], 
            0, layout['left_width']
        )
        
        tree_win = stdscr.subwin(
            layout['tree_height'], 
            layout['side_panel_width'], 
            0, 
            layout['main_width']
        )
        
        properties_win = stdscr.subwin(
            layout['prop_height'], 
            layout['side_panel_width'], 
            layout['tree_height'], 
            layout['main_width']
        )
        
        return left_win, right_win, tree_win, properties_win
    except curses.error:
        # if error in above sizes go to min ones
        left_win = stdscr.subwin(term_height, term_width // 2, 0, 0)
        right_win = stdscr.subwin(term_height, term_width // 2, 0, term_width // 2)
        tree_win = None
        properties_win = None
        return left_win, right_win, tree_win, properties_win

def main(stdscr):
    curses.start_color()
    curses.init_pair(COLOR_TABLE, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    
    term_height, term_width = stdscr.getmaxyx()
    layout = calculate_layout(term_height, term_width)
    left_win, right_win, tree_win, properties_win = create_win(stdscr, layout)
    
    left = WindowState(left_win)
    right = WindowState(right_win)
    left.focused = True
    
    panels = [left, right]
    last_term_size = (term_height, term_width)

    while True:
        # If while in the middle of the program the size of terminal changes
        current_term_height, current_term_width = stdscr.getmaxyx()
        if (current_term_height, current_term_width) != last_term_size:
   
            layout = calculate_layout(current_term_height, current_term_width)
            left_win, right_win, tree_win, properties_win = create_win(stdscr, layout)
            
            left.win = left_win
            right.win = right_win

            for panel in panels:
                panel.rows = []
                panel.data = []
            
            last_term_size = (current_term_height, current_term_width)
            term_height, term_width = current_term_height, current_term_width
        
        stdscr.clear()
        
        for panel in panels:
            render_window(panel, term_height, layout['left_width'] if panel == left else layout['right_width'])
        
        focused_panel = left if left.focused else right
        
        render_side_panel(tree_win, "tree", focused_panel)
        render_side_panel(properties_win, "properties", focused_panel)
        
        status_line = f"W:{term_width} H:{term_height} | Tab=Switch | ↑↓=Navigate | Enter=Open | q=Quit"
        status_text = status_line[:term_width - 1]
        
        stdscr.addstr(term_height - 1, 0, status_text, curses.color_pair(3))

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('\t'):
            left.focused, right.focused = right.focused, left.focused
            continue

        focused_panel = left if left.focused else right
        sort_struck = focused_panel.sort

        new_cursor, new_path, sort_struck = input.handle_key_input(
            key, focused_panel.cursor_row, focused_panel.path, focused_panel.data, focused_panel.sort
        )

        if new_cursor is None:
            break

        if new_cursor is not None:
            focused_panel.cursor_row = new_cursor

        visible_start = focused_panel.scroll_offset
        visible_end = visible_start + (term_height - 3)

        if focused_panel.cursor_row > visible_end:
            focused_panel.scroll_offset = focused_panel.cursor_row - (term_height - 3)
        elif focused_panel.cursor_row < visible_start:
            focused_panel.scroll_offset = focused_panel.cursor_row

        focused_panel.scroll_offset = max(0, min(focused_panel.scroll_offset, len(focused_panel.rows) - 1))

        focused_panel.path = new_path
        focused_panel.sort = sort_struck
        focused_panel.rows = []
        focused_panel.data = []

    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)