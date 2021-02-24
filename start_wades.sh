wades_src_path="/home/silvia/wades"
run_path="/var/lib/wades/run"
ps_handler_file_path="${run_path}/ProcessHandler.pid"
modeller_file_path="${run_path}/Modeller.pid"



while true
  do
    if [ ! -f "${ps_handler_file_path}" ]
    then
      echo $(date -u): ps_handler is not running. Rerunning it.
      sudo python3 "${wades_src_path}/pshandler_starter.py"
      sleep 5s
    fi

    if [ ! -f "${modeller_file_path}" ]
    then
      echo $(date -u): modeller is not running. Rerunning it.
      sudo python3 "${wades_src_path}/modeller_starter.py"
      sleep 5s
    fi

    if [ ! -d "${run_path}/wades_reviver.pid" ]
    then
      echo $$ > "${run_path}/wades_reviver.pid"
    fi
  sleep 5m
  done
