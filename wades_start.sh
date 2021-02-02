virtual_env="${HOME}/wades_env"
activate_bin_path="${HOME}/wades_env/bin/activate"

function create_venv {
  if [ ! -d "${virtual_env}" ];
  then
    echo Creating Virtual environment in "${virtual_env}"
    python3 -m venv "${virtual_env}"
    # shellcheck disable=SC1090
    source "${activate_bin_path}"
    echo Installing dependencies...
    pip3 install -r ./requirements.txt
    echo SUCCESS: Finished installing all dependencies
  else
    echo virtual environment "${virtual_env}" already exists.
  fi || {
  echo Something happened while trying to create venv "${virtual_env}". Cleaning up &&
  rm -rf "${virtual_env}"
  }
}


sudo apt-get install python3-venv
create_venv
python3 ./pshandler_starter.py
python3 ./modeller_starter.py