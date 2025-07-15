import os
import shutil
import sys
import platform
import datetime
import subprocess
import curses
import os
from curses import textpad
from colorama import init, Fore, Style

# Initializing colorama for color output
init(autoreset=True)

version = '1.1'

# Setting up encoding to support the Russian language
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.system("chcp 65001 > nul")

# Glyphs for interface design
GLYPHS = {
    "prompt": "❯",
    "folder": "📁",
    "file": "📄",
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "divider": "─"
}

class TextEditor:
    def __init__(self, filename=None):
        self.filename = filename
        self.lines = []
        self.current_line = 0
        self.current_col = 0
        self.status = ""
        self.unsaved_changes = False
        self.quit = False
        
        if filename and os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
        else:
            self.lines = [""]
            if filename:
                self.status = f"Creating new file: {filename}"

    def run(self, stdscr):
        # Editor config
        curses.curs_set(1)  # Visible cursor
        stdscr.keypad(True)  # Enabling special keys
        stdscr.timeout(10)  # Input timeout for screen refresh
        
        # Editor's Main Cycle
        while not self.quit:
            self.draw_ui(stdscr)
            self.handle_input(stdscr)

    def draw_ui(self, stdscr):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Displaying text with line numbers
        for i, line in enumerate(self.lines[:h-2]):
            line_num = f"{i+1:3d} │ "
            stdscr.addstr(i, 0, line_num, curses.color_pair(1))
            stdscr.addstr(line[:w-len(line_num)-1])
            
            # Highlighting the current line
            if i == self.current_line:
                try:
                    stdscr.chgat(i, len(line_num), len(line), curses.A_REVERSE)
                except:
                    pass
        
        # Status bar
        status_bar = f" {GLYPHS['file']} {self.filename} | String: {self.current_line+1}/{len(self.lines)} | "
        if self.unsaved_changes:
            status_bar += f"{Fore.RED}NOT SAVED{Style.RESET_ALL}"
        else:
            status_bar += "Saved"
            
        stdscr.addstr(h-2, 0, status_bar.ljust(w-1, ' '), curses.color_pair(2))
        
        # Command line
        cmd_line = "PSText | Ctrl+S: Save | Ctrl+Q: Exit | Ctrl+F: Finder"
        stdscr.addstr(h-1, 0, cmd_line.ljust(w-1, ' '), curses.color_pair(3))
        
        # Cursor positioning
        try:
            stdscr.move(
                self.current_line, 
                min(self.current_col + 8, w-1)
            )
        except:
            pass
        
        stdscr.refresh()

    def handle_input(self, stdscr):
        try:
            key = stdscr.getch()
        except:
            return

        if key == -1:
            return

        # Navigation
        if key == curses.KEY_UP:
            self.current_line = max(0, self.current_line - 1)
            self.adjust_column()
        elif key == curses.KEY_DOWN:
            self.current_line = min(len(self.lines)-1, self.current_line + 1)
            self.adjust_column()
        elif key == curses.KEY_LEFT:
            if self.current_col > 0:
                self.current_col -= 1
            elif self.current_line > 0:
                self.current_line -= 1
                self.current_col = len(self.lines[self.current_line])
        elif key == curses.KEY_RIGHT:
            current_line_len = len(self.lines[self.current_line])
            if self.current_col < current_line_len:
                self.current_col += 1
            elif self.current_line < len(self.lines)-1:
                self.current_line += 1
                self.current_col = 0
        elif key == curses.KEY_PPAGE:  # Page Up
            self.current_line = max(0, self.current_line - 10)
            self.adjust_column()
        elif key == curses.KEY_NPAGE:  # Page Down
            self.current_line = min(len(self.lines)-1, self.current_line + 10)
            self.adjust_column()
        
        # Control
        elif key == 10:  # Enter
            # Splitting the row into two
            left = self.lines[self.current_line][:self.current_col]
            right = self.lines[self.current_line][self.current_col:]
            self.lines[self.current_line] = left
            self.lines.insert(self.current_line+1, right)
            self.current_line += 1
            self.current_col = 0
            self.unsaved_changes = True
        elif key == curses.KEY_BACKSPACE:
            if self.current_col > 0:
                # Deleting a character on the left
                line = self.lines[self.current_line]
                self.lines[self.current_line] = line[:self.current_col-1] + line[self.current_col:]
                self.current_col -= 1
                self.unsaved_changes = True
            elif self.current_line > 0:
                # Combining with the previous line
                prev_len = len(self.lines[self.current_line-1])
                self.lines[self.current_line-1] += self.lines[self.current_line]
                del self.lines[self.current_line]
                self.current_line -= 1
                self.current_col = prev_len
                self.unsaved_changes = True
        elif key == curses.KEY_DC:  # Delete
            line = self.lines[self.current_line]
            if self.current_col < len(line):
                self.lines[self.current_line] = line[:self.current_col] + line[self.current_col+1:]
                self.unsaved_changes = True
            elif self.current_line < len(self.lines)-1:
                # Combining with the next line
                self.lines[self.current_line] += self.lines[self.current_line+1]
                del self.lines[self.current_line+1]
                self.unsaved_changes = True
        
        # Keyboard shortcuts
        elif key == 19:  # Ctrl+S (Save)
            self.save_file()
        elif key == 17:  # Ctrl+Q (Exit)
            self.quit = True
        elif key == 6:   # Ctrl+F (Finder)
            self.search(stdscr)
        
        # Ввод текста
        elif 32 <= key <= 126:  # Printable characters
            line = self.lines[self.current_line]
            self.lines[self.current_line] = line[:self.current_col] + chr(key) + line[self.current_col:]
            self.current_col += 1
            self.unsaved_changes = True

    def adjust_column(self):
        """Adjusting the cursor position in the row"""
        current_line_len = len(self.lines[self.current_line])
        if self.current_col > current_line_len:
            self.current_col = current_line_len

    def save_file(self):
        if not self.filename:
            self.status = "Error: Enter file name"
            return

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.lines))
            self.unsaved_changes = False
            self.status = f"File saved: {self.filename}"
        except Exception as e:
            self.status = f"Saving error: {str(e)}"

    def search(self, stdscr):
        """Simple text search"""
        h, w = stdscr.getmaxyx()
        search_str = ""
        cursor_pos = 0
        
        while True:
            stdscr.addstr(h-1, 0, f"Search: {search_str}".ljust(w-1, ' '))
            stdscr.move(h-1, 8 + cursor_pos)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key == 27:  # ESC
                break
            elif key == 10:  # Enter
                self.perform_search(search_str)
                break
            elif key == curses.KEY_BACKSPACE:
                if search_str and cursor_pos > 0:
                    search_str = search_str[:cursor_pos-1] + search_str[cursor_pos:]
                    cursor_pos -= 1
            elif key == curses.KEY_LEFT:
                cursor_pos = max(0, cursor_pos - 1)
            elif key == curses.KEY_RIGHT:
                cursor_pos = min(len(search_str), cursor_pos + 1)
            elif 32 <= key <= 126:  # Printable characters
                search_str = search_str[:cursor_pos] + chr(key) + search_str[cursor_pos:]
                cursor_pos += 1

    def perform_search(self, text):
        """Search for text in a file"""
        if not text:
            return
            
        for i, line in enumerate(self.lines):
            if text in line:
                self.current_line = i
                self.current_col = line.index(text)
                self.status = f"Found in string {i+1}"
                return
                
        self.status = "Text not found"

class Shell:
    def __init__(self):
        self.username = os.getlogin()
        self.hostname = platform.node()
        self.current_dir = os.getcwd()
        self.commands = {
            'help': self.show_help,
            'ls': self.list_dir,
            'dir': self.list_dir,
            'cd': self.change_dir,
            'pwd': self.print_work_dir,
            'mkdir': self.make_dir,
            'rmdir': self.remove_dir,
            'rm': self.remove_file,
            'cp': self.copy_file,
            'mv': self.move_file,
            'cat': self.cat_file,
            'echo': self.echo_text,
            'clear': self.clear_screen,
            'exit': self.exit_shell,
            'ps': self.list_processes,
            'sysinfo': self.system_info,
            'find': self.find_files,
            'size': self.file_size,
            'time': self.show_time,
            'tree': self.show_tree,
            'rename': self.rename_file,
            'grep': self.grep_text,
            'zip': self.zip_file,
            'unzip': self.unzip_file,
            'env': self.show_env,
            'setenv': self.set_env,
            'history': self.show_history,
            'calc': self.calculator,
            'edit': self.edit_file
        }
        self.history = []
        self.session_start = datetime.datetime.now()

    def display_prompt(self):
        dir_name = os.path.basename(self.current_dir) if self.current_dir != os.path.expanduser("~") else "~"
        print(f"\n{Fore.CYAN}{self.username}{Fore.WHITE}@{Fore.GREEN}{self.hostname} {Fore.MAGENTA}{dir_name}")
        print(f"{Fore.RED}{GLYPHS['divider'] * (len(self.username) + len(self.hostname) + len(dir_name) + 2)}")
        print(f"{Fore.BLUE}{GLYPHS['prompt']} {Style.RESET_ALL}", end="")

    def run(self):
        self.clear_screen()
        print(f"{Fore.CYAN}PyShell V1.0 / 2025")
        
        while True:
            try:
                self.display_prompt()
                command = input().strip()
                if not command:
                    continue
                    
                self.history.append(command)
                parts = command.split()
                cmd_name = parts[0].lower()
                args = parts[1:]
                
                if cmd_name in self.commands:
                    self.commands[cmd_name](args)
                else:
                    self.execute_system_command(command)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Stopped by user. For leave enter 'exit'")
            except Exception as e:
                print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def show_help(self, args):
        """Show list of avaible commands"""
        help_text = f"""
{Fore.YELLOW}Avaible commands:{Style.RESET_ALL}

{Fore.CYAN}{GLYPHS['file']}/{GLYPHS['folder']}File operations:{Style.RESET_ALL}
  ls, dir      - Show dir's content
  cd [path]    - Change directory
  pwd          - Print working directory
  mkdir [name]  - Create directory
  rmdir [name]  - Delete directory
  rm [filename]    - Delete file
  cp [file] [another_file] - Copy file/dir
  mv [content] [another_dir] - Move file/dir
  cat [file]   - Show file's content 
  rename [old] [new] - Change file's name
  zip [file]   - Create ZIP-archive
  unzip [.zip]  - Extract ZIP-archive
  size [file]  - Show file's size
  tree - Show the directory tree
  edit [filename] - Edit file 

{Fore.CYAN}🛠System commands:{Style.RESET_ALL}
  ps           - Show process list
  sysinfo      - About system
  env          - Environment variables
  setenv [key] [value] - Set an environment variable
  time         - Show current time
  clear        - Clear screen
  history      - Commands usage history

{Fore.CYAN}⚙Utilities:{Style.RESET_ALL}
  echo [text] - Print text
  find [filename] - Find file 
  grep [text] [file] - Find text in file
  calc [2+2]         - Calculator

{Fore.CYAN}Other:{Style.RESET_ALL}
  help         - Show manual about commands
  exit         - Exit
"""
        print(help_text)

    # Commands implementations
    def list_dir(self, args):
        """Show the contents of a directory with icons"""
        path = args[0] if args else self.current_dir
        try:
            items = os.listdir(path)
            print(f"{Fore.YELLOW}Content {path}:{Style.RESET_ALL}")
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    print(f"{Fore.BLUE}{GLYPHS['folder']} {item}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}{GLYPHS['file']} {item}{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}{GLYPHS['error']} Directory not found: {path}")

    def change_dir(self, args):
        """Change directory"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter path")
            return
            
        path = args[0]
        try:
            if path == "..":
                os.chdir("..")
            elif path == "~":
                os.chdir(os.path.expanduser("~"))
            else:
                os.chdir(path)
            self.current_dir = os.getcwd()
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def print_work_dir(self, args):
        """Show the current working directory"""
        print(f"{Fore.CYAN}Current directory: {self.current_dir}")

    def make_dir(self, args):
        """Create directory"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter directory name")
            return
            
        dir_name = args[0]
        try:
            os.makedirs(dir_name, exist_ok=True)
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def remove_dir(self, args):
        """Delete directory"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter directory name")
            return
            
        dir_name = args[0]
        try:
            shutil.rmtree(dir_name)
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def remove_file(self, args):
        """Delete file"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter file name")
            return
            
        file_name = args[0]
        try:
            os.remove(file_name)
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def copy_file(self, args):
        """Copy file/directory"""
        if len(args) < 2:
            print(f"{Fore.RED}{GLYPHS['error']} Enter correct values")
            return
            
        src, dest = args[0], args[1]
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
            print(f"{Fore.GREEN}{GLYPHS['success']} Copied!: {src} -> {dest}")
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error {str(e)}")

    def move_file(self, args):
        """Move file/directory"""
        if len(args) < 2:
            print(f"{Fore.RED}{GLYPHS['error']} Enter correct values")
            return
            
        src, dest = args[0], args[1]
        try:
            shutil.move(src, dest)
            print(f"{Fore.GREEN}{GLYPHS['success']} Moved!: {src} -> {dest}")
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def cat_file(self, args):
        """Show file's content"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter file name")
            return
            
        file_name = args[0]
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                print(f"{Fore.YELLOW}File's content {file_name}:{Style.RESET_ALL}")
                print(f.read())
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def echo_text(self, args):
        """Print text"""
        print(" ".join(args))

    def clear_screen(self, args=None):
        """Clear screen"""
        os.system("cls")

    def exit_shell(self, args=None):
        """Exit from shell"""
        duration = datetime.datetime.now() - self.session_start
        os.system('cls')
        print(f"{Fore.MAGENTA}Session duration: {duration}")
        sys.exit(0)

    # Additional commands
    def list_processes(self, args):
        """List of running processes"""
        try:
            output = subprocess.check_output("tasklist", shell=True, encoding="cp866")
            print(output)
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def system_info(self, args):
        """About system"""
        info = f"""
{Fore.CYAN}About system:{Style.RESET_ALL}
  System: {platform.system()} {platform.release()}
  CPU: {platform.processor()}
  Architecture: {platform.architecture()[0]}
  User: {self.username}
  Working directory: {self.current_dir}
  Start time: {self.session_start}
"""
        print(info)

    def find_files(self, args):
        """Find files by template"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter template for search")
            return
            
        pattern = args[0]
        found = False
        for root, dirs, files in os.walk(self.current_dir):
            for name in files + dirs:
                if pattern.lower() in name.lower():
                    print(os.path.join(root, name))
                    found = True
        if not found:
            print(f"{Fore.YELLOW}{GLYPHS['warning']} File/s not found")

    def file_size(self, args):
        """Show file size"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter file name")
            return
            
        file_name = args[0]
        try:
            size = os.path.getsize(file_name)
            print(f"{Fore.CYAN}File size: {size} байт ({size/1024:.2f} KB)")
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def show_time(self, args):
        """Current time"""
        now = datetime.datetime.now()
        print(f"{Fore.CYAN}Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    def show_tree(self, args):
        """Show directory tree"""
        try:
            os.system("tree")
        except:
            print(f"{Fore.YELLOW}{GLYPHS['warning']} Command 'tree' doesn't support by Your system")

    def rename_file(self, args):
        """Rename file"""
        if len(args) < 2:
            print(f"{Fore.RED}{GLYPHS['error']} Enter old and new file names")
            return
            
        old_name, new_name = args[0], args[1]
        try:
            os.rename(old_name, new_name)
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def grep_text(self, args):
        """Search text in file"""
        if len(args) < 2:
            print(f"{Fore.RED}{GLYPHS['error']} Enter text and file name")
            return
            
        text, file_name = args[0], args[1]
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if text in line:
                        print(f"{Fore.CYAN}String {i+1}:{Style.RESET_ALL} {line.strip()}")
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def zip_file(self, args):
        """Create ZIP archive"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter file/dir name")
            return
            
        source = args[0]
        archive = source + ".zip"
        try:
            shutil.make_archive(source, 'zip', os.path.dirname(source), os.path.basename(source))
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def unzip_file(self, args):
        """Extract ZIP archive"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter archive name")
            return
            
        archive = args[0]
        try:
            shutil.unpack_archive(archive, os.path.splitext(archive)[0])
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Error: {str(e)}")

    def show_env(self, args):
        """Show environment variables"""
        for key, value in os.environ.items():
            print(f"{Fore.CYAN}{key}{Style.RESET_ALL}={value}")

    def set_env(self, args):
        """Set an environment variable"""
        if len(args) < 2:
            print(f"{Fore.RED}{GLYPHS['error']} Enter key and value")
            return
            
        key, value = args[0], args[1]
        os.environ[key] = value
        print(f"{Fore.GREEN}{GLYPHS['success']} Setted!: {key}={value}")

    def show_history(self, args):
        """Show commands history"""
        for i, cmd in enumerate(self.history):
            print(f"{i+1}: {cmd}")

    def calculator(self, args):
        """Simple calculator"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Enter Expression (example: 2+2)")
            return
            
        try:
            expression = " ".join(args)
            result = eval(expression)
            print(f"{Fore.CYAN}Result: {result}")
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Calculation error: {str(e)}")
            
    def edit_file(self, args):
        """Запуск текстового редактора"""
        if not args:
            print(f"{Fore.RED}{GLYPHS['error']} Укажите имя файла")
            return
            
        filename = args[0]
        try:
            # Проверяем, установлен ли curses для Windows
            if os.name == 'nt':
                try:
                    import curses
                except ImportError:
                    print(f"{Fore.RED}Для работы редактора установите windows-curses: pip install windows-curses")
                    return
            
            # Инициализация цветов
            curses.initscr()
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Номера строк
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Статус бар
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Командная строка
            
            # Запуск редактора
            editor = TextEditor(filename)
            editor.run(curses.initscr())
            
            # Восстановление терминала
            curses.endwin()
            
            print(f"{Fore.GREEN}{GLYPHS['success']} Файл сохранен" if not editor.unsaved_changes else 
                  f"{Fore.YELLOW}{GLYPHS['warning']} Выход без сохранения")
        except Exception as e:
            curses.endwin()
            print(f"{Fore.RED}{GLYPHS['error']} Ошибка редактора: {str(e)}")

    def execute_system_command(self, command):
        """Run system command"""
        try:
            result = subprocess.run(
                command, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{Fore.RED}{result.stderr}")
        except Exception as e:
            print(f"{Fore.RED}{GLYPHS['error']} Run error: {str(e)}")

if __name__ == "__main__":
    shell = Shell()
    shell.run()
