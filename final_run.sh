#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

if [ $? -eq 0 ]; then
    echo "Activated virtual environment."
    
    # Install requirements
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "Installed requirements."
        
        # Check if pm2 is required
        if ! command -v pm2 &> /dev/null; then
            echo "pm2 is not installed. Installing..."
            
            # Check if npm is installed
            if ! command -v npm &> /dev/null; then
                echo "npm is not installed. Installing..."
                
                # Check if node is installed
                if ! command -v node &> /dev/null; then
                    echo "node is not installed. Installing..."
                    brew install node
                fi
                
                # Install npm
                brew install npm
            fi
            
            # Install pm2
            npm install pm2@latest -g
        fi
        
        # Start the Django project with pm2
        pm2 start echosystem.config.json
    else
        echo "Failed to install requirements."
    fi
else
    echo "Failed to activate virtual environment."
fi

