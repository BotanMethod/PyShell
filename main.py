import os
import shutil
import sys
import platform
import datetime
import subprocess
from colorama import init, Fore, Style

# Initializing colorama for color output
init(autoreset=True)

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
            'mkfile': self.make_file,
            'rm': self.remove_file,
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
            'calc': self.calculator
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

{Fore.CYAN}File operations:{Style.RESET_ALL}
  ls, dir      - Show dir's content
  cd [path]    - Change directory
  pwd          - Print working directory
  mkdir [name]  - Create directory
  rmdir [name]  - Delete directory
  mkfile [name] - Create file
  rm [filename]    - Delete file
  cp [file] [another_file] - Copy file/dir
  mv [content] [another_dir] - Move file/dir
  cat [file]   - Show file's content 
  rename [old] [new] - Change file's name
  zip [file]   - Create ZIP-archive
  unzip [.zip]  - Extract ZIP-archive
  size [file]  - Show file's size
  tree         - Show the directory tree

{Fore.CYAN}System commands:{Style.RESET_ALL}
  ps           - Show process list
  sysinfo      - About system
  env          - Environment variables
  setenv [key] [value] - Set an environment variable
  time         - Show current time
  clear        - Clear screen
  history      - Commands usage history

{Fore.CYAN}Utilities:{Style.RESET_ALL}
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
