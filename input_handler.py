import os
import curses
import shutil

def handle_key_input(key:int, cursor_row:int, directory:str, data:list, sort_def:str) -> tuple[int, str, str]:
    max_cursor = 3 + (len(data) * 2)

    if key == curses.KEY_UP and cursor_row > 3:
        return cursor_row - 2, directory, sort_def  # Move up
    elif key == curses.KEY_DOWN and cursor_row < max_cursor - 2:
        return cursor_row + 2, directory, sort_def  # Move down
    elif key == ord('q'):
        return None, None, None
    elif key == curses.KEY_DC:
        data_index = (cursor_row - 3) // 2
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))

            if os.path.isdir(selected_path):
                shutil.rmtree(selected_path ,ignore_errors = True)    
            else:
                os.remove(selected_path)        
        return cursor_row , directory, sort_def
    elif key == ord('s'):
        return cursor_row, directory, 's'
    elif key == ord('a'):
        return cursor_row, directory, 'a'
    elif key == ord('m'):
        return cursor_row, directory, 'm'
    elif key == curses.KEY_LEFT:
        return 3, os.path.dirname(directory), sort_def # Move back
    elif key == 10:  # Enter key
        data_index = (cursor_row - 3) // 2
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))

            if os.path.isdir(selected_path):
                return 3, selected_path, sort_def  # Navigate into folder
            else:
                os.system(f"xdg-open '{selected_path}'")
                return cursor_row, directory, sort_def  # Stay in the same directory
    return cursor_row, directory, sort_def # Default case (no change)
