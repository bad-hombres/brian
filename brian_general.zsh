export LISTS_LOCATION=$BRIAN_HOME/lists
export TOOLS_DIR=$BRIAN_HOME/tools
export PROJECT_DIR=${PWD}

mkdir -p subdomains sources triggers sinks pipelines

[[ ! -f domains.txt ]] && touch domains.txt 
[[ ! -f subdomains/start ]] && touch subdomains/start

python3 $BRIAN_HOME/generate.py
source shell_functions.zsh
reset

