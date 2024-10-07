#!/bin/bash

CONFIG_FILE="./config.ini"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file '$CONFIG_FILE' not found."
    exit 1
fi

source "$CONFIG_FILE"

model_path="$tora_model_path"

folder_name=$1
source "$conda_activate_path" tora
cd "$tora_src_path"
bash ./scripts/infer_tora.sh $folder_name $model_path 
