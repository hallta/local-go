# Import required Flask modules and JSON for configuration handling
from flask import Flask, abort,request, redirect
import json

# Initialize Flask application
app = Flask(__name__)
# Dictionary to store path-to-URL mappings in memory
redir_map = {}

# Custom 404 error handler
@app.errorhandler(404)
def not_found(e):
    return "URL not found"

# Special route to view all configured redirects
# Access via /go/👀
@app.route("/go/👀")
def show_config():
    return json.dumps(redir_map, indent=2)

# Main redirect route
# Handles requests like /go/gh -> redirects to configured URL
@app.route("/go/<string:path>")
def go(path):
    if path in redir_map:
        return redirect("https://" + redir_map[path], code=302)
    else:
        abort(404)

# Endpoint to save new redirect mappings
# Usage: /save?p=shortcut&u=url
# Example: /save?p=gh&u=github.com
@app.route('/save')
def save():
    # Get path (shortcut) and URL from query parameters
    path = request.args.get('p')
    url = request.args.get('u')
    # Store in memory
    redir_map[path] = url

    # Append to config file for persistence
    config = open('config', 'a')
    config.write(path + ':' + url + "\n")
    config.close()

    return "👍"

# Load redirect mappings from config file into memory
def load_config():
    with open("config", "r") as config:
        for option in config:
            # Split each line into path and URL
            path, url = option.split(':', 1)
            # Store in memory, removing trailing newline
            redir_map[path] = url.rstrip()

# Initialize the application by loading config
def startup():
    load_config()

# Run startup when module is imported
startup()
