import redis
import os

r = redis.Redis(host = "localhost", port = 6379, decode_responses=True)

def cache_size(path):
    
    if r.get(path):
        return r.get(path)

    total_size = 0
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_symlink():
                    continue
                if entry.is_file(follow_symlinks=False):
                    total_size += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    total_size += cache_size(entry.path)
    except PermissionError:
        pass 
    r.set(path, total_size)
    return total_size 

if __name__ == "__main__":
    
    r.flushall()
    cache_size("/")
