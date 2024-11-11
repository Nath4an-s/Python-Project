import subprocess

# Initialize a new PowerShell process in a separate console window
debug_ps = subprocess.Popen(
    ["powershell.exe", "-NoExit", "-Command", "-"],
    stdin=subprocess.PIPE,
    text=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE  # Forces a new console window
)

def debug_print(message):
    """Send debug messages to the new PowerShell window."""
    if debug_ps.stdin:
        # Use Write-Host to ensure output appears in PowerShell
        debug_ps.stdin.write(f"Write-Host '[DEBUG] {message}'\n")
        debug_ps.stdin.flush()

# Ensure the PowerShell window closes when the script exits
def close_logger():
    if debug_ps.stdin:
        debug_ps.stdin.write("exit\n")
        debug_ps.stdin.close()
        debug_ps.wait()
