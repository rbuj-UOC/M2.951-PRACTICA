#!/usr/bin/env bash

# Other possible shebangs:
##!/bin/bash
##!/opt/homebrew/bin/bash
##!/usr/local/bin/bash

# maximum number of parallel processes
NPROCS=6

# mkdir logs
mkdir -p logs

for i in {1..365}; do
    DAY=$(date -v-"${i}"d +"%d.%m.%Y")
    python3 source/main.py -d 1 -b "${DAY}" -m >logs/"${DAY}".log &
    # run at most NPROCS processes in parallel, use wait -n to
    # wait for one to finish before launching another
    while [ $(jobs -r | wc -l) -ge ${NPROCS} ]; do
        wait -n
    done
    # wait a moment before launching the next process
    sleep 1
done

wait
python3 source/main.py -w >logs/merge.log
