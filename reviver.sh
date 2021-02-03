run_path="${HOME}/.wades/run"
ps_handler_file_path="${run_path}/ProcessHandler.pid"
modeller_file_path="${run_path}/Modeller.pid"

echo $$ > "${HOME}/.wades/run/wades_reviver.pid"

while true
  do
    if [ ! -f "${ps_handler_file_path}" ]
    then
      echo ps_handler is not running. Rerunning it.
      python3 ./pshandler_starter.py
    fi

    if [ ! -f "${modeller_file_path}" ]
    then
      echo modeller is not running. Rerunning it.
      python3 ./modeller_starter.py
    fi
  sleep 5m
  done
