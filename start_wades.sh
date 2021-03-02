wades_src_path="/home/silvia/wades"
run_path="/var/lib/wades/run"
wades_daemon_file_path="${run_path}/WadesDaemon.pid"



while true
  do
    if [ ! -f "${wades_daemon_file_path}" ]
    then
      echo "$(date -u): wades daemon is not running. Rerunning it."
      sudo python3 "${wades_src_path}/wades.py" start
      sleep 5s
    fi

    if [ ! -d "${run_path}/wades_reviver.pid" ]
    then
      echo $$ > "${run_path}/wades_reviver.pid"
    fi
  sleep 5m
  done
