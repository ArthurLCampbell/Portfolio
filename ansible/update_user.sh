#!/bin/bash

#set -e
set -o pipefail
#set -x

# Define items to update
ITEM_LIST=(
	"/home/user/.config/i3"
	"/home/user/.config/polybar"
	"/home/user/.config/kitty"

	"/home/user/.zsh"
	"/home/user/.zshrc")

# Keep count
ITEM_LIST_TOTAL="${#ITEM_LIST[@]}"
ITEM_LIST_COUNT=0

# Iterate over items to update entries to new user
for ITEM in "${ITEM_LIST[@]}"
do
	ITEM_LIST_COUNT=$(( ITEM_LIST_COUNT + 1 ))
	printf "[ %s / %s ] Updating %s\n" "${ITEM_LIST_COUNT}" "${ITEM_LIST_TOTAL}" "${ITEM}"
	
	while read -r LINE
	do
		if [ -e "${LINE}" ]
		then
			printf "%s\n" "${LINE}"
			sed -i 's/\/home\/insight/\/home\/user/g' "${LINE}"
		else
			printf "%s not found. Skipping.\n" "${LINE}"
		fi
	done < <(find "${ITEM}" -type f)
done
