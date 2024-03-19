from flask import Flask, abort,request, redirect
import json

app = Flask(__name__)
redir_map = {}

@app.errorhandler(404)
def not_found(e):
    return "URL not found"


@app.route("/go/👀")
def show_config():
    return json.dumps(redir_map, indent=2)


@app.route("/go/<string:path>")
def go(path):
    if path in redir_map:
        return redirect("https://" + redir_map[path], code=302)
    else:
        abort(404)


@app.route('/save')
def save():
    path = request.args.get('p')
    url = request.args.get('u')
    redir_map[path] = url

    config = open('config', 'a')
    config.write(path + ':' + url + "\n")
    config.close()

    return "👍"



def load_config():
    with open("config", "r") as config:
        for option in config:
            path, url = option.split(':', 1)
            redir_map[path] = url.rstrip()


def startup():
    load_config()

startup()
