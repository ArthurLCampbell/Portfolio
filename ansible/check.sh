#!/bin/bash

#set -e
set -o pipefail
set -x

# Define directory to use
ANSI_DIR="/home/insight/code/ansible"

if [ ! -d "${ANSI_DIR}" ]
then
	printf "%s not found.\n" "${ANSI_DIR}"
	exit 1
fi

# Define list to use and store results
FILE_LIST=()

# Iterate over items.
while read -r LINE
do
	FILE_LIST+=("${LINE}")
done < <(find "${ANSI_DIR}" -iname "*.yaml" -type f)

FILE_COUNT=0
FILE_TOTAL="${#FILE_LIST[@]}"

for FILE in "${FILE_LIST[@]}"
do
	FILE_COUNT=$(( FILE_COUNT + 1 ))

	echo "[ ${FILE_COUNT} / ${FILE_TOTAL} ] Checking ${FILE}"
	ansible-playbook --syntax-check "${FILE}"
done
