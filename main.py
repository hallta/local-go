# Import required Flask modules and JSON for configuration handling
from flask import Flask, abort, request, redirect
import json
from typing import Dict, Optional
from pathlib import Path

# Initialize Flask application
app = Flask(__name__)
# Dictionary to store path-to-URL mappings in memory
redirect_map: Dict[str, str] = {}
CONFIG_FILE = Path("config")

# Custom 404 error handler
@app.errorhandler(404)
def not_found(_) -> str:
    return "URL not found"

# Special route to view all configured redirects
# Access via /go/👀
@app.route("/go/👀")
def show_config() -> str:
    return json.dumps(redirect_map, indent=2)

# Main redirect route
# Handles requests like /go/gh -> redirects to configured URL
@app.route("/go/<string:path>")
def go(path: str):
    if path in redirect_map:
        return redirect(f"https://{redirect_map[path]}", code=302)
    abort(404)

# Endpoint to save new redirect mappings
# Usage: /save?p=shortcut&u=url
# Example: /save?p=gh&u=github.com
@app.route('/save')
def save() -> str:
    # Get path (shortcut) and URL from query parameters
    shortcut: Optional[str] = request.args.get('p')
    url: Optional[str] = request.args.get('u')
    
    if not all([shortcut, url]):
        abort(400, "Missing required parameters 'p' (shortcut) or 'u' (url)")
    
    # Store in memory
    redirect_map[shortcut] = url

    # Append to config file for persistence
    with CONFIG_FILE.open('a') as config:
        config.write(f"{shortcut}:{url}\n")

    return "👍"

# Load redirect mappings from config file into memory
def load_config() -> None:
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()
        return
        
    with CONFIG_FILE.open("r") as config:
        for line in config:
            try:
                shortcut, url = line.strip().split(':', 1)
                redirect_map[shortcut] = url
            except ValueError:
                # Skip malformed lines
                continue

# Initialize the application by loading config
def startup() -> None:
    load_config()

# Run startup when module is imported
startup()
