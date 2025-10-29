#!/bin/bash
## nombre maxim de processos en paral·lel
NPROCS=6

for i in {1..365}
do
   DAY=$(date -v-${i}d +"%d.%m.%Y")
   python3 source/main.py -d 1 -b ${DAY} -m > ${DAY}.log &
   ## executa com a molt NPROCS processos a la vegada, utilitza wait -n per esperar que acabi un abans de llançar-ne un altre
   while [ $(jobs -r | wc -l) -ge ${NPROCS} ]; do
       wait -n
   done
   ## Espera un moment abans de llançar el següent procés
   sleep 1
done

wait
python3 source/main.py -w > merge.log
