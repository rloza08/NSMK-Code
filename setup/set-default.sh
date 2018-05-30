#!/bin/bash
cp cli-selections.json ../../config
rm cli-selections.json
cp safeway-config.json ../../config
rm safeway-config.json
cp *.json ../../templates
echo "default settings have been set."