sudo pip3 install -r ./requirements.txt
sudo cp ./wades.service /etc/systemd/system/wades.service
sudo systemctl daemon-reload
sudo systemctl start wades
sudo systemctl enable wades
