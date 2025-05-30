import os
import curses
import shutil

clipboard = {
    'items': [],
    'operation': None 
}

def handle_key_input(key: int, cursor_row: int, directory: str, data: list, sort_def: str) -> tuple[int, str, str]:
    
    data_rows = []
    for i, row in enumerate(data):
        data_rows.append(3 + (i * 2))
    
    if key == curses.KEY_UP and cursor_row > 3:

        current_data_index = -1
        for i, row_pos in enumerate(data_rows):
            if row_pos == cursor_row:
                current_data_index = i
                break
        
        if current_data_index > 0:
            return data_rows[current_data_index - 1], directory, sort_def
        return cursor_row, directory, sort_def
    
    elif key == curses.KEY_DOWN and len(data_rows) > 0:

        current_data_index = -1
        for i, row_pos in enumerate(data_rows):
            if row_pos == cursor_row:
                current_data_index = i
                break
        
        if current_data_index >= 0 and current_data_index < len(data_rows) - 1:
            return data_rows[current_data_index + 1], directory, sort_def
        elif current_data_index == -1 and len(data_rows) > 0:

            return data_rows[0], directory, sort_def
        return cursor_row, directory, sort_def
    
    elif key == ord('q'):
        return None, None, None
    
    elif key == curses.KEY_DC:  # Delete key
        data_index = get_data_index_from_cursor(cursor_row, data)
        
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))

            try:
                if os.path.isdir(selected_path):
                    shutil.rmtree(selected_path, ignore_errors=True)    
                else:
                    os.remove(selected_path)
            except (OSError, PermissionError):
                pass 
        
        return cursor_row, directory, sort_def
   
    elif key == ord('c'):  # Copy
        data_index = get_data_index_from_cursor(cursor_row, data)
        
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))
            
            clipboard['items'] = [selected_path]
            clipboard['operation'] = 'copy'
        
        return cursor_row, directory, sort_def
    
    elif key == ord('x'):  # Cut
        data_index = get_data_index_from_cursor(cursor_row, data)
        
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))
            
            clipboard['items'] = [selected_path]
            clipboard['operation'] = 'cut'
        
        return cursor_row, directory, sort_def
    
    elif key == ord('v'):  # Paste
        if clipboard['items'] and clipboard['operation']:
            for source_path in clipboard['items']:
                if os.path.exists(source_path):
                    filename = os.path.basename(source_path)
                    destination_path = os.path.join(directory, filename)
                    
                    counter = 1
                    original_destination = destination_path
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(original_destination)
                        destination_path = f"{name}_copy_{counter}{ext}"
                        counter += 1
                    
                    try:
                        if clipboard['operation'] == 'copy':
                            if os.path.isdir(source_path):
                                shutil.copytree(source_path, destination_path)
                            else:
                                shutil.copy2(source_path, destination_path)
                        
                        elif clipboard['operation'] == 'cut':
                            shutil.move(source_path, destination_path)
                    
                    except (OSError, PermissionError, shutil.Error):
                        pass 
            
            if clipboard['operation'] == 'cut':
                clipboard['items'] = []
                clipboard['operation'] = None
        
        return cursor_row, directory, sort_def
    
    elif key == ord('s'):  # Sort by size
        return cursor_row, directory, 's'
   
    elif key == ord('a'):  # Sort alphabetically
        return cursor_row, directory, 'a'
   
    elif key == ord('m'):  # Sort by modification date
        return cursor_row, directory, 'm'
   
    elif key == curses.KEY_LEFT:  # Go back
        return 3, os.path.dirname(directory), sort_def
   
    elif key == 10:  # Enter key
        data_index = get_data_index_from_cursor(cursor_row, data)
   
        if 0 <= data_index < len(data):
            selected_entry = data[data_index][0]
            selected_path = os.path.join(directory, selected_entry.lstrip('/'))

            if os.path.isdir(selected_path):
                return 3, selected_path, sort_def  # Navigate into folder
            else:
                try:
                    os.system(f"xdg-open '{selected_path}'")
                except:
                    pass  
                return cursor_row, directory, sort_def 
   
    return cursor_row, directory, sort_def  # Default case (no change)

def get_data_index_from_cursor(cursor_row: int, data: list) -> int:

    if cursor_row < 3:
        return -1

    data_index = (cursor_row - 3) // 2
    return data_index if data_index < len(data) else -1
