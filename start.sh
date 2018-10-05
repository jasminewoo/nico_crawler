#!/usr/bin/env bash

if [[ ! -d venv ]]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip3 install -r requirements.txt
python3 nico_crawler.py
deactivate
