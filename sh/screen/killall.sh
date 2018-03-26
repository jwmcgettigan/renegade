#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -e "${GREEN}BEFORE${NC}"
screen -list
screen -X -S teleop quit
screen -X -S run quit
echo -e "${RED}AFTER${NC}"
screen -list
