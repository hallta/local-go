# local-go

Mini redirector service

# Run

1. `python3 -m venv env`
1. `source env/bin/activate`
1. `flask --app amin run`

# Configiure

1. `127.0.0.1/go/<url>` will work
1. Configure a Chrome search to "go"
1. Save new urls either at the `config` file or at `/save?p=%s&u=%s`
