#!/bin/bash

# Script to push Multi-Hop Research Agent to new NSK-AI-Hackathon repository

echo "Setting up new repository: NSK-AI-Hackathon"

# Add new remote for NSK-AI-Hackathon repository
git remote add nsk-hackathon https://github.com/Oghenesuvwe-dev/NSK-AI-Hackathon.git

# Push the Multi-Hop-Research-Agent branch to the new repository as main
git push -u nsk-hackathon Multi-Hop-Research-Agent:main

echo "Project pushed to NSK-AI-Hackathon repository!"
echo "Repository URL: https://github.com/Oghenesuvwe-dev/NSK-AI-Hackathon"