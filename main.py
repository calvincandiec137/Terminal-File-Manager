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
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)  # status
   
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    sort='a'
    sort_def=sort
    
    current_path = os.getcwd()
    
    cursor_row = 3 
    scroll_offset = 0 
    
    while True:
    
        stdscr.clear()
        terminal_height, terminal_width = stdscr.getmaxyx()
    
        directory_data = file.gather_directory_data(current_path, sort)
        headers = file.generate_headers(current_path, terminal_width)
        rows = tabulate.tabulate(directory_data, headers=headers, tablefmt="grid", maxcolwidths=[None, 18]).splitlines()
        
        max_displayable_rows = terminal_height - 2  # 2 for keybinds
        total_rows = len(rows)
        
        max_scroll = max(0, total_rows - max_displayable_rows)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        # Calculate which rows to display
        start_row = scroll_offset
        end_row = min(start_row + max_displayable_rows, total_rows)
        
        # Display the visible portion of the table
        display_row = 0
        for i in range(start_row, end_row):
            if display_row >= max_displayable_rows - 1:  # Leave space for status
                break
                
            row = rows[i]
            truncated_row = row[:terminal_width - 1]
           
            try:
                # Check if this is the cursor row (accounting for scroll)
                if i == cursor_row:
                    stdscr.addstr(display_row, 0, truncated_row, curses.color_pair(config.COLOR_HIGHLIGHT) | curses.A_REVERSE)
                else:
                    stdscr.addstr(display_row, 0, truncated_row, curses.color_pair(config.COLOR_TABLE))
                display_row += 1
            except curses.error:
                break
        
        # Display status line with scroll information
        if total_rows > max_displayable_rows:
            scroll_info = f"[{scroll_offset + 1}-{min(scroll_offset + max_displayable_rows, total_rows)}/{total_rows}]"
            status_line = f"Delete=Remove, ↑↓=Navigate, Enter=Open, q=Quit, c=Copy, x=Cut, v=Paste, {scroll_info}"
        else:
            status_line = "Delete=Remove, ↑↓=Navigate, Enter=Open, q=Quit, c=Copy, x=Cut, v=Paste"
        
        try:
            stdscr.addstr(terminal_height - 1, 0, status_line[:terminal_width-1], curses.color_pair(3))
        except curses.error:
            pass
        
        stdscr.refresh()
        key = stdscr.getch()
        
        # Handle scrolling keys
        if key == curses.KEY_PPAGE:  # Page Up
            scroll_offset = max(0, scroll_offset - max_displayable_rows + 3)
            # Adjust cursor if it's now off screen
            if cursor_row < scroll_offset:
                cursor_row = max(3, scroll_offset)
            continue
            
        elif key == curses.KEY_NPAGE:  # Page Down
            scroll_offset = min(max_scroll, scroll_offset + max_displayable_rows - 3)
            # Adjust cursor if it's now off screen
            if cursor_row >= scroll_offset + max_displayable_rows:
                cursor_row = min(scroll_offset + max_displayable_rows - 1, len(rows) - 1)
            continue
        
        # Handle regular navigation
        sort_struck = sort_def
        new_cursor, new_path, sort_struck = input.handle_key_input(key, cursor_row, current_path, directory_data, sort_def)
        
        if new_cursor is None:
            break 

        # Update cursor and handle auto-scrolling
        if new_cursor is not None:
            old_cursor = cursor_row
            cursor_row = new_cursor
            
            # Auto-scroll logic
            visible_start = scroll_offset
            visible_end = scroll_offset + max_displayable_rows - 1
            
            # If cursor moved below visible area, scroll down
            if cursor_row > visible_end:
                scroll_offset = cursor_row - max_displayable_rows + 1
                
            # If cursor moved above visible area, scroll up
            elif cursor_row < visible_start:
                scroll_offset = cursor_row
                
            # Ensure scroll_offset stays within bounds
            scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        current_path, sort = new_path, sort_struck
        sort_def = sort
        
    curses.endwin()


if __name__ == "__main__":
    import curses
    curses.wrapper(main)