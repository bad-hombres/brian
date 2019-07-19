export LISTS_LOCATION=$BRIAN_HOME/lists
export TOOLS_DIR=$BRIAN_HOME/tools
export PROJECT_DIR=${PWD}

mkdir -p subdomains sources triggers sinks pipelines
touch domains.txt subdomains/start
python $BRIAN_HOME/generate.py

