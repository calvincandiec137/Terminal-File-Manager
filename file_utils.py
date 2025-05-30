import os
import time

dir_cache={}

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
    
    sort_key = {'a':0, 's':1, 'm': 2}
    data = []

    for entry in os.listdir(directory):
        if entry.startswith('.'):
            continue
        
        entry_path = os.path.join(directory, entry)
        entry_name = f"/{entry}" if os.path.isdir(entry_path) else entry
       # entry_size = get_folder_size(entry_path) if os.path.isdir(entry_path) else os.path.getsize(entry_path)
       # modify_date = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(os.path.getmtime(entry_path)))

        data.append([entry_name])  

    data.sort(key=lambda x: x[sort_key[sort]])

   # for item in data:
   #     item[1] = format_size(item[1])  

    return data


def generate_headers(directory, terminal_width):

    return [
        f"{directory:<{terminal_width-10}}"]
