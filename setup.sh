#!/bin/bash

echo "Installing CBC Solver..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update && sudo apt install -y coinor-cbc
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install cbc
else
    echo "Please install CBC manually."
fi

echo "CBC Installation Complete!"