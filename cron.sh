#!/bin/sh

# Get script folder
# tmp_dir=$(readlink -f "$0")
# tmp_dir=$(dirname "$tmp_dir")
# root dir where the files for the build are located
# build_dir=$(readlink -f "$tmp_dir/")
# cd "$build_dir"

cd ~/public_html/moldowinebot/
python index.py "{\"action\": \"run_cron\"}"
