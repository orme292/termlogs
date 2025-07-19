# Termlogs

---

Termlogs parses iTerm2 session logs to show session logs by timespan.

## Configure iTerm2
1. In preferences, go to Profiles
2. Select profile (or Default)
3. Click Session tab
4. Tick `Enable automatic session logging`
5. Set Log format to `Plain text`
6. Set Folder

## Create configuration file
1. Create file `~/.termlogs`
2. Add the following to the `.termlogs` file:
3. Don't use quotes or any symbols around the session_logs_path

```ini
[settings]
session_logs_path = <session log directory>
```

### Function/alias to call termlogs:
Add this function to your `~/.zprofile` or `~/.bash_profile` to 
run termlogs from anywhere.
```bash
termlogs () {
  (
    export curdir=$(pwd)
    cd /Users/myuser/github/termlogs/ || exit
    source .venv/bin/activate
    python3 /Users/myuser/github/termlogs/main.py "$@"
    cd $curdir
  )
}
```