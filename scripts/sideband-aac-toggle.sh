#!/bin/bash

enabled=$(git config --global --get sideband.allowControlCharacters)

if [[ "$enabled" == "true" ]]; then
    git config --global --unset sideband.allowControlCharacters

    if [[ $? -eq 0 ]]; then
        echo "sideband.allowControlCharacters has been disabled."
    else
        echo "Failed to disable sideband.allowControlCharacters."
    fi
else
    git config --global sideband.allowControlCharacters true

    if [[ $? -eq 0 ]]; then
        echo "sideband.allowControlCharacters has been enabled."
    else
        echo "Failed to enable sideband.allowControlCharacters."
    fi
fi
