#!/bin/bash

set -e
set -o pipefail
set -x

ansible -m setup all
