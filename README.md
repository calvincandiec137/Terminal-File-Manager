# List Manager

A terminal-based file explorer with a clean, interactive interface built in Python. This utility allows users to navigate through directories, view file/folder sizes, and access files directly from the terminal.

## Features

- Interactive terminal user interface using curses library
- Directory navigation with size calculation for files and folders
- Clean tabulated display with:
  - File/folder names
  - Sizes (automatically formatted to B, KB, MB, GB, TB)
  - Creation/modification dates
- Color-coded interface for better visibility
- Keyboard navigation support
- Direct file opening capability using system default applications

## Requirements

- Python 3.x
- Required Python packages:
  - `tabulate`
  - `curses` (typically comes with Python)
- Linux-based system (for `xdg-open` functionality)

## Installation

### For Debian-based Systems (.deb)

1. Download the .deb package:
```bash
wget https://github.com/yourusername/list-manager/releases/download/v1.0/list-manager.deb
```

2. Install the package:
```bash
sudo dpkg -i list-manager.deb
sudo apt-get install -f  # Install dependencies if needed
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/list-manager.git
```

2. Install required packages:
```bash
pip install tabulate
```

3. Make the script executable:
```bash
chmod +x list.py
```

## Usage

### Navigation

- **Up Arrow**: Move cursor up
- **Down Arrow**: Move cursor down
- **Left Arrow**: Go to parent directory
- **Enter**: 
  - On folders: Enter the directory
  - On files: Open with default application
- **q**: Quit the application

### Running the Program

```bash
./list.py
```

or

```bash
python3 list.py
```

## Future Development

1. **File Operations**
   - Copy/Cut/Paste functionality
   - Delete files/folders
   - Create new files/folders
   - Rename files/folders

2. **UI Enhancements**
   - File preview capability
   - Custom color themes
   - Sort by different columns
   - Search functionality
   - File filtering options

3. **Performance Improvements**
   - Asynchronous directory size calculation
   - Caching for frequently accessed directories
   - Optimize large directory handling

4. **Cross-platform Support**
   - Windows compatibility
   - macOS compatibility
   - Custom file opener for different platforms

5. **Additional Features**
   - Bookmark favorite directories
   - File compression/extraction
   - Multiple pane view
   - File permission management
   - Git integration for repositories

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Known Issues

- Large directories may take time to load due to size calculation
- Currently only supports Linux-based systems for file opening
- Hidden files are not displayed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the `tabulate` library for the clean table formatting
- Inspired by traditional file managers like Midnight Commander
