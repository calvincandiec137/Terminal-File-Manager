#!/usr/bin/python3
import curses
import os
import tabulate
import file_utils as file
import input_handler as input
import config

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
                panel.win.addstr(i - start_row, 0, row, curses.color_pair(config.COLOR_HIGHLIGHT) | curses.A_REVERSE)
            else:
                panel.win.addstr(i - start_row, 0, row, curses.color_pair(config.COLOR_TABLE))
        except curses.error:
            break

def render_side_panel(subpanel, panel_type="tree", focused_panel=None):
    subpanel.clear()
    height, width = subpanel.getmaxyx()
    
    try:
        # Draw border
        for i in range(height):
            if i == 0:
                border_str = f"╭{'─' * (width - 2)}╮"
                subpanel.addstr(i, 0, border_str[:width], curses.color_pair(config.COLOR_TABLE))
            elif i == height - 1:
                border_str = f"╰{'─' * (width - 2)}╯"
                subpanel.addstr(i, 0, border_str[:width], curses.color_pair(config.COLOR_TABLE))
            else:
                subpanel.addstr(i, 0, "│", curses.color_pair(config.COLOR_TABLE))
                if width > 1:
                    subpanel.addstr(i, width - 1, "│", curses.color_pair(config.COLOR_TABLE))
        
        # Add title and content
        if panel_type == "tree":
            title = " Tree "
            if width >= len(title):
                title_x = (width - len(title)) // 2
                subpanel.addstr(0, title_x, title, curses.color_pair(config.COLOR_TABLE))
            
            # Show current directory
            if focused_panel and height > 3 and width > 4:
                current_dir = os.path.basename(focused_panel.path) or "/"
                display_dir = current_dir[:width - 4] if len(current_dir) > width - 4 else current_dir
                subpanel.addstr(2, 2, display_dir, curses.color_pair(config.COLOR_TABLE))
                
                # Show parent directories if space allows
                if height > 4:
                    parent = os.path.dirname(focused_panel.path)
                    if parent and parent != focused_panel.path:
                        parent_name = os.path.basename(parent) or "/"
                        display_parent = f"../{parent_name}"[:width - 4]
                        subpanel.addstr(3, 2, display_parent, curses.color_pair(3))
        
        else:  # Properties panel
            title = " Props "
            if width >= len(title):
                title_x = (width - len(title)) // 2
                subpanel.addstr(0, title_x, title, curses.color_pair(config.COLOR_TABLE))
            
            # Show selected item properties
            if focused_panel and focused_panel.data and height > 3 and width > 4:
                data_index = focused_panel.cursor_row - 3
                if 0 <= data_index < len(focused_panel.data):
                    item = focused_panel.data[data_index]
                    if item:
                        line = 2
                        # Item name
                        name = str(item[0])[:width - 4]
                        subpanel.addstr(line, 2, name, curses.color_pair(config.COLOR_TABLE))
                        line += 1
                        
                        # Item size
                        if len(item) > 1 and line < height - 1:
                            size = str(item[1])[:width - 4]
                            subpanel.addstr(line, 2, size, curses.color_pair(3))
                            line += 1
                        
                        # Item date
                        if len(item) > 2 and line < height - 1:
                            date = str(item[2])[:width - 4]
                            subpanel.addstr(line, 2, date, curses.color_pair(3))
    
    except curses.error:
        pass
    
    subpanel.refresh()

def calculate_layout(term_height, term_width):

    # Minimum sizes 
    MIN_PANEL_WIDTH = 20
    MIN_SIDE_PANEL_WIDTH = 15
    MIN_HEIGHT = 10
    
    # use minimal if terminal too small
    if term_width < 60 or term_height < 20:
        side_panel_width = max(MIN_SIDE_PANEL_WIDTH, term_width // 6)
        main_width = term_width - side_panel_width
        left_width = main_width // 2
        right_width = main_width - left_width
    else:
        side_panel_width = max(MIN_SIDE_PANEL_WIDTH, min(term_width*2 // 5, 50))
        main_width = term_width - side_panel_width
        left_width = main_width // 2
        right_width = main_width - left_width
    
    tree_height = max(MIN_HEIGHT // 2, term_height // 2) - 2 # -2 cuz the right left panel are of not full lenght
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
    curses.init_pair(config.COLOR_TABLE, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(config.COLOR_HIGHLIGHT, curses.COLOR_WHITE, curses.COLOR_BLUE)
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
        try:
            stdscr.addstr(term_height - 1, 0, status_text, curses.color_pair(3))
        except curses.error:
            pass

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