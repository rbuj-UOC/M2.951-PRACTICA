#!/usr/bin/env bash

# Altres shebangs possibles:
##!/bin/bash
##!/opt/homebrew/bin/bash
##!/usr/local/bin/bash

# Estableix el nom de la carpeta a partir del directori actual
WORK_DIR=${PWD}
FOLDER=$(basename ${WORK_DIR})

# Elimina el fitxer .DS_Store que crea macOS en cada carpeta
find . -name ".DS_Store" -exec rm "{}" \;

# Canvia al directori superior per crear l'arxiu comprimit
cd ..

# Elimina l'arxiu si ja existeix
if [ -f ${FOLDER}.tar.zst ]; then
    rm ${FOLDER}.tar.zst
fi

# Comprimeix la carpeta en un fitxer .tar.zst
tar --zstd -cvf ${FOLDER}.tar.zst \
    --exclude="${FOLDER}/.git" \
    --exclude="${FOLDER}/.venv" \
    --exclude="${FOLDER}/__pycache__" \
    ${FOLDER}