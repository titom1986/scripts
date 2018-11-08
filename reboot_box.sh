#!/bin/bash

# CONFIGURATION
IP="192.168.0.1"
user="titom"
password="+gVPSe2a"

# Connection a l'interface
wget -q -P /dev/null --post-data="loginUsername=${user}&loginPassword=${password}" --no-check-certificate --delete-after https://${IP}/goform/login

# Appel de la page pour reboot
wget -q -P /dev/null --tries=1 --header="Origin:https://${IP}" --header="Referer: https://${IP}/config.html" --post-data "" --no-check-certificate https://${IP}/goform/WebUiOnlyReboot
