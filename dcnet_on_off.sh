#!/bin/bash

#script by scrivanidc 20250124
echo "DCNET Server ON/OFF Script Switch"
echo ""
echo "Choose option number"
echo "1. DCNET Script ON"
echo "2. DCNET Script OFF (Standard DreamPi)"
read -p "Type 1 or 2 and press Enter: " opcao

cd /home/pi/dreampi/
echo ""
verificar_arquivo_a() {
  if [ ! -f "dreampi_dcnet.py" ]; then
    echo "dreampi_dcnet.py backup and dcnet.rpi does not exist. Downloading..."
    echo ">>"
    wget -O dreampi_dcnet.py https://github.com/flyinghead/flycast/raw/refs/heads/dev/tools/dreampi/dreampi.py
    wget https://github.com/flyinghead/flycast/raw/refs/heads/dev/tools/dreampi/dcnet.rpi
    chmod +x dreampi_dcnet.py dcnet.rpi
  else
    echo "dreampi_dcnet.py and dcnet.rpi exists. OK."
    echo ">>"
  fi
}

verificar_arquivo_b() {
  if [ ! -f "dreampi_standard.py" ]; then
    echo "dreampi_standard.py backup does not exist. Creating..."
    cp dreampi.py dreampi_standard.py
    cp dreampi.py dreampi_standard2.py
  else
    echo "dreampi_standard.py backup exists. OK."
    echo ">>"
  fi
}

copiar_arquivo_a() {
  cp dreampi_dcnet.py dreampi.py
  echo "dreampi_dcnet.py copied to dreampi.py"
  echo ">>"
}

copiar_arquivo_b() {
  cp dreampi_standard.py dreampi.py
  echo "dreampi_standard.py copied to dreampi.py"
  echo ">>"
}

verificar_arquivo_b
verificar_arquivo_a

if [ "$opcao" -eq 1 ]; then
  copiar_arquivo_a
  echo "Done. DCNET Script ON (Standard DreamPi Script disabled)"
elif [ "$opcao" -eq 2 ]; then
  copiar_arquivo_b
  echo "Done. DCNET Script OFF (Standard DreamPi Script enabled)"
else
  echo "Invalid option. Please choose 1 or 2."
fi

sudo service dreampi restart &
echo ">>"
echo "Restarting Modem, ready to dial soon"
