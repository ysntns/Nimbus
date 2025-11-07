#!/bin/bash

##############################################################################
# Nimbus GitHub Deploy Script
# 
# This script initializes git, creates a private repo, and pushes to GitHub
#
# Author: Yasin TANIŞ
##############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Nimbus GitHub Deployment Script${NC}\n"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Check if gh CLI is installed (for creating private repo)
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) is not installed.${NC}"
    echo -e "${YELLOW}   Install with: sudo apt install gh${NC}"
    echo -e "${YELLOW}   Or visit: https://cli.github.com/${NC}\n"
    
    read -p "Do you want to continue without creating a new repo? (y/n): " continue_choice
    if [[ $continue_choice != "y" ]]; then
        exit 0
    fi
else
    # Check if logged in to GitHub
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}⚠️  You are not logged in to GitHub CLI${NC}"
        echo "Please login with: gh auth login"
        exit 1
    fi
    
    CREATE_REPO=true
fi

# Initialize git repository
echo -e "${GREEN}📦 Initializing Git repository...${NC}"
git init

# Add all files
echo -e "${GREEN}📝 Adding files to Git...${NC}"
git add .

# Create initial commit
echo -e "${GREEN}💾 Creating initial commit...${NC}"
git commit -m "Initial commit: Nimbus v2.0.0

- Complete backup engine with incremental support
- CLI interface with rich output
- Configuration management system
- Multi-threading support
- Verification and checksums
- Test suite
- Documentation
- CI/CD pipeline

Created by Yasin TANIŞ - CerebrAI-VorTX
"

# Rename branch to main
git branch -M main

# Create GitHub repository if gh CLI is available
if [[ $CREATE_REPO == true ]]; then
    echo -e "\n${GREEN}🌟 Creating private GitHub repository...${NC}"
    gh repo create nimbus --private --source=. --description="Enterprise Backup & Cloud Sync Solution for Linux" --push
    
    echo -e "\n${GREEN}✅ Repository created and pushed successfully!${NC}"
    echo -e "${GREEN}🔗 Repository URL: https://github.com/ysntns/nimbus${NC}\n"
else
    echo -e "\n${YELLOW}⚠️  Manual steps required:${NC}"
    echo "1. Create a new private repository on GitHub: https://github.com/new"
    echo "2. Name it: nimbus"
    echo "3. Make it private"
    echo "4. Run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/ysntns/nimbus.git"
    echo "   git push -u origin main"
    echo ""
fi

echo -e "${GREEN}📊 Repository Status:${NC}"
git log --oneline -5
echo ""

echo -e "${GREEN}🎉 Deployment script completed!${NC}\n"
