#!/usr/bin/env bash

#./worker/bin/bb8 files | entr sh -c "export PYTHONPATH=`pwd` && ./worker/bin/bb8 sync"

if [ ! -e worker ]; then
  echo Setup
  virtualenv worker
  ./worker/bin/pip install -e .
fi

./worker/bin/bb8 sync
