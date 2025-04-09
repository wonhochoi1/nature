#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up nature-env conda environment...${NC}"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "conda could not be found. Please install Anaconda or Miniconda first."
    exit 1
fi

# Create the conda environment
echo -e "${YELLOW}Creating conda environment 'nature-env'...${NC}"
conda create -y -n nature-env python=3.9

# Activate the environment
echo -e "${YELLOW}Activating environment...${NC}"
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate nature-env

# Install pip packages from requirements.txt
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Print success message and instructions
echo -e "${GREEN}Nature environment setup complete!${NC}"
echo -e "${YELLOW}To activate the environment, run:${NC}"
echo -e "conda activate nature-env"
echo -e "${YELLOW}To run the web sandbox, run:${NC}"
echo -e "cd sandbox"
echo -e "python app.py"
echo -e "${YELLOW}Don't forget to set your OpenAI API key:${NC}"
echo -e "export OPENAI_API_KEY=your_api_key_here" 