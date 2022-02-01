#!/bin/bash

#set -e
set -o pipefail
set -x

# Ping all hosts defined
ansible all -m ping
