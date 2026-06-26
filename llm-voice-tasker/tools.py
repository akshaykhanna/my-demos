import os
import subprocess
import glob
import webbrowser
import urllib.parse

def find_start_menu_app(app_name: str) -> str:
    """Searches Windows Start Menu directories for a matching shortcut (.lnk) file."""
    app_query = app_name.lower().strip()
    
    # Common Windows Start Menu paths
    user_start_menu = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
    system_start_menu = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    
    search_paths = [user_start_menu, system_start_menu]
    
    for path in search_paths:
        if os.path.exists(path):
            # Find all shortcut (.lnk) files recursively
            shortcuts = glob.glob(os.path.join(path, "**", "*.lnk"), recursive=True)
            for shortcut in shortcuts:
                shortcut_name = os.path.basename(shortcut).lower()
                # Check if the app name is in the shortcut filename (e.g., "spotify" in "spotify.lnk")
                if app_query in shortcut_name:
                    return shortcut
    return None

def open_application(app_name: str) -> str:
    """Tries to launch any installed application on the system dynamically."""
    print(f"  [Tool] Dynamically searching for application: '{app_name}'")
    
    # 1. Search Start Menu shortcuts
    shortcut_path = find_start_menu_app(app_name)
    if shortcut_path:
        try:
            print(f"  [Tool] Found Start Menu shortcut: '{shortcut_path}'")
            os.startfile(shortcut_path)  # Opens the shortcut (.lnk) using the OS
            return f"Successfully opened '{app_name}'."
        except Exception as e:
            return f"Found shortcut but failed to open: {e}"
            
    # 2. Fallback: Try launching directly via Windows shell command
    try:
        print(f"  [Tool] Shortcut not found. Trying direct Windows shell start for '{app_name}'...")
        subprocess.Popen(f"start {app_name}", shell=True)
        return f"Successfully executed start command for '{app_name}'."
    except Exception as e:
        return f"Error: Application '{app_name}' is not installed, or could not be found."

def search_download_page(app_name: str) -> str:
    """Opens a web browser to Google to find download pages for missing applications."""
    print(f"  [Tool] Opening browser search for '{app_name}' download link...")
    query = f"download {app_name}"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    try:
        webbrowser.open(search_url)
        return f"Successfully opened browser to search for download links for '{app_name}'."
    except Exception as e:
        return f"Failed to open browser: {e}"

# Expose tools dictionary
TOOLS = {
    "open_application": open_application,
    "search_download_page": search_download_page
}
