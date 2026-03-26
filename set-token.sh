#!/bin/bash
echo "Enter your GitHub Personal Access Token:"
read -s TOKEN
git config --global credential.helper 'cache --timeout=86400'
echo "https://pallavi-dhadage:$TOKEN@github.com" > ~/.git-credentials
echo "Token configured. It will be cached for 24 hours."
