#!/bin/bash

etc_path=$(dirname $(readlink -f "$0"))
if [ "$(whoami)" != "root" ]; then
  echo "Error: raspiot-server must run as root user!"
  exit 1
fi

cd ${etc_path}
supervisord -c ${etc_path}/supervisord.conf
