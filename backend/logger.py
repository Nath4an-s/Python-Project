import subprocess
import os
from datetime import datetime

debug_ps = subprocess.Popen(
    ["powershell.exe", "-NoExit", "-Command", "-"],
    stdin=subprocess.PIPE,
    text=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE  
)

log_file_path = os.path.join(os.getenv('TEMP'), 'gamelogs.txt')

header_printed = False

debug_ps = subprocess.Popen(
    ["powershell.exe", "-NoExit", "-Command", "-"],
    stdin=subprocess.PIPE,
    text=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE  
)

log_file_path = os.path.join(os.getenv('TEMP'), 'gamelogs.txt')

header_printed = False

def debug_print(message):
    global header_printed

    # Format current time with seconds
    session_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if not header_printed:
        if debug_ps.stdin:
            debug_ps.stdin.write(f"Write-Host 'Game Log (session: {session_date}) : '\n")
            debug_ps.stdin.flush()

        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Game Log (session: {session_date})\n")
        
        header_printed = True

    if debug_ps.stdin:
        debug_ps.stdin.write(f"Write-Host '>> {message}'\n")
        debug_ps.stdin.flush()

    with open(log_file_path, 'a') as log_file:
        log_file.write(f"> {message} - {session_date}\n")


def close_logger():
    if debug_ps.stdin:
        debug_ps.stdin.write("exit\n")
        debug_ps.stdin.close()
        debug_ps.wait()


def close_logger():
    if debug_ps.stdin:
        debug_ps.stdin.write("exit\n")
        debug_ps.stdin.close()
        debug_ps.wait()

print(f"Log file path: {log_file_path}")