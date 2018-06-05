#!/bin/bash
cp cli-selections.json ../../config
cp safeway-config.json ../../config
cp *.json ../../templates
cp *.csv /appl/nms/xfer
rm ../../templates/cli-selections.json
rm ../../templates/safeway-config.json
echo "default settings have been set."
