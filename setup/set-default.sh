#!/bin/bash
cp cli-selections.json ../../config
cp safeway-config.json ../../config
cp *.json ../../templates
rm ../../templates/cli-selections.json
rm ../../templates/safeway-config.json
echo "default settings have been set."
