#!/bin/bash

#script by scrivanidc 20250124

echo "Choose option number"
echo "1. DCNET Script ON"
echo "2. DCNET Script OFF (Standard DreamPi)"
read -p "Type 1 or 2: " opcao

cd /home/pi/dreampi/

verificar_arquivo_a() {
  if [ ! -f "arquivo_b" ]; then
    echo "dreampi_dcnet.py backup and dcnet.rpi does not exist. Downloading..."
    wget https://github.com/................./dreampi_dcnet.py
    wget https://github.com/................./dcnet.rpi
    chmod +x dreampi_dcnet.py dcnet.rpi
  else
    echo "dreampi_dcnet.py and dcnet.rpi exists. OK."
  fi
}

verificar_arquivo_b() {
  if [ ! -f "dreampi_standard.py" ]; then
    echo "dreampi_standard.py backup does not exist. Creating..."
    cp dreampi.py dreampi_standard.py
  else
    echo "dreampi_standard.py backup exists. OK."
  fi
}

copiar_arquivo_a() {
  cp dreampi_dcnet.py dreampi.py
  echo "dreampi_dcnet.py copied to dreampi.py"
}

copiar_arquivo_b() {
  cp dreampi_standard.py dreampi.py
  echo "dreampi_standard.py copied to dreampi.py"
}

verificar_arquivo_a
verificar_arquivo_b

if [ "$opcao" -eq 1 ]; then
  copiar_arquivo_a
elif [ "$opcao" -eq 2 ]; then
  copiar_arquivo_b
else
  echo "Invalid option. Please choose 1 or 2."
fi

sudo service dreampi restart &
