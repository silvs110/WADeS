sudo kill "$(cat "/var/lib/wades/run/wades_reviver.pid")" || echo "Process is not running."
sudo python3 ./stop_daemons.py
