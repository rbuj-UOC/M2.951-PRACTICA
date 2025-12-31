#!/usr/bin/env bash

# Other possible shebangs:
##!/bin/bash
##!/opt/homebrew/bin/bash
##!/usr/local/bin/bash

# parse command line options
GENERATE_PDF=true
GENERATE_HTML=true
UPDATE_ONLY=false
while getopts "h-:" opt; do
    case "$opt" in
        -)
            case "${OPTARG}" in
                pdf)
                    GENERATE_HTML=false
                    ;;
                html)
                    GENERATE_PDF=false
                    ;;
                help)
                    echo "Usage: $0 [--pdf] [--html]"
                    echo "  --pdf    Generate only PDF report"
                    echo "  --html   Generate only HTML report"
                    exit 0
                    ;;
                *)
                    echo "Invalid option: --${OPTARG}"
                    exit 1
                    ;;
            esac
            ;;
        h)
            echo "Usage: $0 [--pdf] [--html]"
            echo "  --pdf    Generate only PDF report"
            echo "  --html   Generate only HTML report"
            exit 0
            ;;
        *)
            echo "Invalid option: -${opt}"
            exit 1
            ;;
    esac
done

# clean up previous reports
rm -fr informe_* informe.html.zip informe.html informe.pdf

# update R packages
# Rscript -e "update.packages(ask = FALSE, checkBuilt = TRUE, repos = 'https://cran.rediris.es/')"

if [ "$GENERATE_PDF" = true ]; then
    echo "Generating PDF report..."
    Rscript -e "rmarkdown::render('informe.Rmd', output_format = 'pdf_document')"
    # if the previous command failed, exit with error
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi

if [ "$GENERATE_HTML" = true ]; then
    echo "Generating HTML report..."
    Rscript -e "rmarkdown::render('informe.Rmd', output_format = 'html_document')"
    # if the previous command succeeded, zip the HTML file
    if [ $? -eq 0 ]; then
        zip informe.html.zip informe.html
    fi
fi