#!/usr/bin/env bash

# Other possible shebangs:
##!/bin/bash
##!/opt/homebrew/bin/bash
##!/usr/local/bin/bash

# Function to display help
help_func() {
    echo "Usage: init.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message and exit"
    echo "  -v, --verbose       Enable verbose output"
    echo "  -q, --quiet         Disable verbose output"
    echo ""
}

# parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --help|-h) help_func; exit 0 ;;
        --verbose|-v) set -x ;;
        --quiet|-q) set +x ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

TARGET_DIR=".venv"
if [ -d "$TARGET_DIR" ]; then
    echo "Directory $TARGET_DIR already exists. Please remove it before running this script."
    exit 1
fi

# set up virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt