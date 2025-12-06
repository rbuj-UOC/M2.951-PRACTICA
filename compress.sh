#!/usr/bin/env bash

# Other possible shebangs:
##!/bin/bash
##!/opt/homebrew/bin/bash
##!/usr/local/bin/bash

# function to compress the current working directory excluding certain files and folders
compress_folder() {
    # Set the working directory and folder name
    WORK_DIR=${PWD}
    FOLDER=$(basename "${WORK_DIR}")
    ARCHIVE=${FOLDER}.tar.zst
    # Remove .DS_Store
    find . -name ".DS_Store" -exec rm "{}" \;
    # Change to the parent directory to create the compressed file
    cd ..
    # Remove the file if it already exists
    if [ -f "${ARCHIVE}" ]; then
        rm "${ARCHIVE}"
    fi
    # Compress the folder into a .tar.zst file
    tar --zstd -cvf "${ARCHIVE}" \
        --exclude="${FOLDER}/.git" \
        --exclude="${FOLDER}/.venv" \
        --exclude="${FOLDER}/__pycache__" \
        --exclude="${FOLDER}/*.tar.zst" \
        --exclude="${FOLDER}/*.tar.xz" \
        --exclude="${FOLDER}/logs" \
        --exclude="${FOLDER}/dataset" \
        "${FOLDER}"
    # Change back to the original working directory
    cd "${WORK_DIR}" || exit
}

# function to compress the logs folder
compress_logs() {
    FOLDER=logs
    ARCHIVE=${FOLDER}.tar.xz
    # Remove .DS_Store
    find . -name ".DS_Store" -exec rm "{}" \;
    # Remove the file if it already exists
    if [ -f ${ARCHIVE} ]; then
        rm ${ARCHIVE}
    fi
    # Compress the folder into a .tar.zst file
    tar --zstd -cvf ${ARCHIVE} \
        --exclude="${FOLDER}/merged.log" \
        ${FOLDER}
}

# function to compress the dataset folder
compress_dataset() {
    FOLDER=dataset
    ARCHIVE=${FOLDER}.tar.xz
    # Remove .DS_Store
    find . -name ".DS_Store" -exec rm "{}" \;
    # Remove the file if it already exists
    if [ -f ${ARCHIVE} ]; then
        rm ${ARCHIVE}
    fi
    # Compress the folder into a .tar.xz file
    tar -cJvf ${ARCHIVE} \
        --exclude="${FOLDER}/*_merged.csv" \
        --exclude="${FOLDER}/dataset.csv" \
        ${FOLDER}
}

# check if no arguments are provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. Use --help or -h for usage information."
    exit 1
fi

# parse arguments --folder or -f, --logs or -l, --dataset or -d, --help or -h.
FOLDER=false
LOGS=false
DATASET=false
for option in "$@"; do
    case $option in
    --folder | -f)
        FOLDER=true
        shift
        ;;
    --logs | -l)
        LOGS=true
        shift
        ;;
    --dataset | -d)
        DATASET=true
        shift
        ;;
    --help | -h)
        echo "Usage: compress.sh [--folder|-f] [--logs|-l] [--dataset|-d]"
        echo "  --folder, -f   Compress the current working directory excluding certain files and folders."
        echo "  --logs, -l     Compress the 'logs' folder excluding the merged.log file."
        echo "  --dataset, -d  Compress the 'dataset' folder excluding merged and dataset CSV files."
        exit 0
        ;;
    *)
        echo "Invalid argument. Use --help or -h for usage information."
        exit 1
        ;;
    esac
done

if [ "$FOLDER" = true ]; then
    # Call the folder compression function
    compress_folder
fi

if [ "$LOGS" = true ]; then
    # Call the logs compression function
    compress_logs
fi

if [ "$DATASET" = true ]; then
    # Call the dataset compression function
    compress_dataset
fi
