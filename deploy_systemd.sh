DEST=/lib/systemd/system/
F=wonderland-power_meter@.service
sudo cp -v $F $DEST 
sudo chmod 644 $DEST/$F 
sudo systemctl daemon-reload
sudo systemctl enable $F 
