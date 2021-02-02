kill "$(cat "${HOME}/.wades/run/wades_reviver.pid")" || echo "Process is not running."
python3 ./stop_daemons.py