#!/bin/bash

cd ~/vive_pptgen_be

source venv/bin/activate

pip install -r requirements.txt

pkill -f uvicorn || true 

nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

