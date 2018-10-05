#!/usr/bin/env bash

pid=`ps aux | grep crawler.py | grep -v grep | awk '{print $2}'`

if [ $pid -ne 0 ]; then
    kill $pid
fi
