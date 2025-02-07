#!/bin/bash

#script by scrivanidc 202500206
echo "DCNET Server ON/OFF Script Switch"
echo ""
echo "Choose option number"
echo "1. DCNET Script ON"
echo "2. DCNET Script OFF (Standard DreamPi)"
echo "3. Delete DCNET Files"
read -p "Type 1, 2 or 3 and press Enter: " opcao

cd /usr/local/bin/
echo ""
verificar_arquivo_a() {
  if [ ! -f "dreampi_dcnet" ]; then
    echo "dreampi_dcnet backup and dcnet.rpi does not exist. Downloading..."
    echo ">>"
    wget -q --show-progress -O dreampi_dcnet https://github.com/scrivanidc/dreampi_custom_scripts/raw/refs/heads/main/DCNET_VM/dreampi
    wget -q --show-progress -O dcnet.rpi https://github.com/scrivanidc/dreampi_custom_scripts/raw/refs/heads/main/DCNET_VM/dcnet.rpi
    chmod +x dreampi_dcnet dcnet.rpi
  else
    echo "dreampi_dcnet and dcnet.rpi exists. OK."
    echo ">>"
  fi
}

verificar_arquivo_b() {
  if [ ! -f "dreampi_standard" ]; then
    echo "dreampi_standard backup does not exist. Creating..."
    cp dreampi dreampi_standard
    cp dreampi dreampi_standard2
  else
    echo "dreampi_standard backup exists. OK."
    echo ">>"
  fi
}

copiar_arquivo_a() {
  cp dreampi_dcnet dreampi
  echo "dreampi_dcnet copied to dreampi"
  echo ">>"
}

copiar_arquivo_b() {
  cp dreampi_standard dreampi
  echo "dreampi_standard copied to dreampi"
  echo ">>"
}

deletar_arquivo_a() {
  copiar_arquivo_b
  rm dreampi_dcnet dcnet.rpi
  echo "deleting DCNET files: dreampi_dcnet and dcnet.rpi"
  echo "You're now able to download DCNET updated files at option 1"
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
elif [ "$opcao" -eq 3 ]; then
  deletar_arquivo_a 
  echo "Done. DCNET files deleted"
else
  echo "Invalid option. Please choose 1, 2 or 3."
fi

sudo service dreampi restart &
echo ">>"
echo "Restarting Modem, ready to dial soon"
