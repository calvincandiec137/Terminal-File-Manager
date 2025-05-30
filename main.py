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

    max_displayable_rows = height - 2
    total_rows = len(panel.rows)
    max_scroll = max(0, total_rows - max_displayable_rows)
    panel.scroll_offset = max(0, min(panel.scroll_offset, max_scroll)) #when scroll tries to go beyond max scroll it seits min to max_scrool then we choose max max_scroll 

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
            


def main(stdscr):
    curses.start_color()
    curses.init_pair(config.COLOR_TABLE, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(config.COLOR_HIGHLIGHT, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    term_height, term_width = stdscr.getmaxyx()
    mid = term_width // 2

    left_win = stdscr.subwin(term_height, 55, 0, 0)
    right_win = stdscr.subwin(term_height, term_width - mid, 0, 51)

    left = WindowState(left_win)
    right = WindowState(right_win)
    left.focused = True

    panels = [left, right]

    while True:
        stdscr.clear()

        for panel in panels:
            render_window(panel, term_height, 55)
        
        status_line = f"Delete=Remove, ↑↓=Navigate, Enter=Open, q=Quit, c=Copy, x=Cut, v=Paste"
        try:
            stdscr.addstr(term_height - 1, 0, status_line[:55 - 1], curses.color_pair(3))
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
