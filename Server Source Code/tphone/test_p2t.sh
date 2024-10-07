#!/bin/bash

CONFIG_FILE="./config.ini"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file '$CONFIG_FILE' not found."
    exit 1
fi

source "$CONFIG_FILE"

image_path=$1
image_quality=$2
source "$conda_activate_path" p2t
cd "$Tphone_path"
python test_p2t.py --image_path "$image_path" --image_quality "$image_quality"
