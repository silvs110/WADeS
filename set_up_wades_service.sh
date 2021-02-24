sudo ./wades_src/setup.sh
sudo cp ./wades.service /etc/systemd/system/wades.service
sudo systemctl start wades
sudo systemctl enable wades
