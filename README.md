# local-go

Mini redirector service

# Run

1. `python3 -m venv env`
1. `source env/bin/activate`
1. `pip install -r /path/to/requirements.txt`
1. `flask --app main run`

# Configiure

1. `127.0.0.1/go/<url>` will work
1. Configure a Chrome search to "go"
1. Save new urls either at the `config` file or at `/save?p=%s&u=%s`

# Usage

## Quick Access
- Type `go <shortcut>` in your browser's address bar to quickly access saved URLs
- Example: `go gh` might redirect to `https://github.com`

## Adding New Shortcuts
1. Visit `http://127.0.0.1:5000/save?p=<shortcut>&u=<url>`
   - Replace `<shortcut>` with your desired shortcut (e.g., "gh")
   - Replace `<url>` with the full URL you want to redirect to
2. Or edit the `config` file directly to add new mappings

## Examples
- `go gh` → `https://github.com`
- `go docs` → `https://docs.python.org`
- `go local` → `http://localhost:3000`
