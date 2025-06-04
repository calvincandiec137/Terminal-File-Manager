
# Terminal File Manager

A terminal-based file manager written in Python using `curses`.  
It supports browsing directories, viewing file properties, and basic file operations like copy, cut, paste, and delete — all with keyboard navigation.

---

## Features

- Dual-panel layout for easy directory comparison  
- Directory tree view and file property panels  
- Keyboard navigation (arrow keys, Tab for switching panels)  
- File operations: copy, cut, paste, delete  
- Sort files by name, size, or modification date  
- Open files with default system application  
- Dynamic layout adapts to terminal resizing  
- Directory size caching using Redis for improved performance  

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/terminal-file-manager.git
   cd terminal-file-manager
    ```

2. **Install dependencies:**

   * Python 3.6+ required
   * Install required packages via pip:

     ```bash
     pip install tabulate redis
     ```

3. **Install and start Redis server:**

   * On Linux (Ubuntu/Debian):

     ```bash
     sudo apt-get install redis-server
     sudo systemctl start redis
     sudo systemctl enable redis
     ```

   * On macOS with Homebrew:

     ```bash
     brew install redis
     brew services start redis
     ```

   * Ensure Redis is running on `localhost:6379`.

4. **Run the program:**

   ```bash
   python3 main.py
   ```

---

## Usage

### Navigation

* Use **Up (↑)** and **Down (↓)** arrow keys to move the cursor within the current panel.
* Press **Tab** to switch focus between the left and right panels.
* Press **Enter** on a directory to navigate inside it.
* Press **Left (←)** arrow key to go up to the parent directory.
* Press **q** to quit the application.

### File Operations

* **Delete:** Press `Delete` key to delete the selected file or directory.
* **Copy:** Press `c` to copy the selected file/directory.
* **Cut:** Press `x` to cut the selected file/directory.
* **Paste:** Press `v` to paste the copied/cut file/directory into the current directory.

### Viewing Information

* The right side panels display:

  * A file tree showing the directory contents.
  * Properties panel showing detailed information about the selected file/folder such as:

    * Name, path, size (in KB)
    * Creation and modification timestamps
    * File permissions

---

## Caching with Redis

This file manager uses Redis to cache directory sizes, improving performance by avoiding repeated recursive size calculations.


**Important:**

* Redis server must be running on `localhost:6379` before running the application.
* Cache is flushed on each program start to avoid stale data.
* Directory access permissions may affect size caching.

---

## File Structure

* `main.py`: Main entry point and UI rendering logic.
* `input_handler.py`: Handles key inputs and file operations.
* `file_utils.py`: Utility functions for gathering directory data, calculating folder sizes, etc.
* `subpanel.py`: Renders side panels like file properties and git info.
* `requirements.txt`: Lists Python dependencies.

---

## Screenshots

*(Add your screenshots here showing the dual-panel UI, navigation, and side panels)*

---

## Notes

* Tested on Linux with Python 3.8+.
* Requires a terminal supporting curses.
* Opening files relies on `xdg-open` on Linux (modify as needed for other OS).
* Permissions and deletion operations depend on your user's rights.
* Redis server must be installed and running for directory size caching.

---

## Contribution

Feel free to fork and submit pull requests for improvements or bug fixes.

---

## Contact

For questions or support, open an issue or contact me at [iam1divide0@gmail.com](mailto:iam1divide0@gmail.com).


