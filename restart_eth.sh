#!/bin/bash

if ! (( $(ifconfig eth0 | grep -q "inet addr:") )) ;
then
        ifup --force eth0
fi
