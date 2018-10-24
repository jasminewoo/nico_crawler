#!/usr/bin/env bash

action=$1

if [ ${action} == "start" ] ; then
    if [[ ! -d venv ]]; then
        python3 -m venv venv
    fi

    if [[ -d logs ]]; then
        rm -r logs
    fi

    source venv/bin/activate
    pip3 install -r requirements.txt
    python3 nico_crawler.py
    deactivate
elif [ ${action} == "download" ] ; then
    url=$2
    if [[ ! -d requests ]]; then
        mkdir requests
    fi

    timestamp=`date +%s`
    echo ${url} > requests/${timestamp}
elif [ ${action} == "kill" ] ; then
    pid=`ps aux | grep crawler.py | grep -v grep | awk '{print $2}'`
    if [ ${pid} -ne 0 ]; then
        kill ${pid}
    fi
elif [ ${action} == "gd" ] ; then
    # TODO: get the user to authenticate
    # TODO: create directory
    # TODO : save to config_secret.json
    echo "Coming soon...\n"
else
    echo "Not recognized action: ${action}"
fi
