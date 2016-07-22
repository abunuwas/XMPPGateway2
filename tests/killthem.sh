#!/bin/bash

processes=$(pgrep python)

for p in $processes
  do
  	kill -9 $p
done
