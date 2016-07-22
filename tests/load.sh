#!/bin/bash

source ../venv/bin/activate

python component_connection.py &

for i in {0..100..1}
  do
  	python client_connection.py $i &
  	echo $i
 done
