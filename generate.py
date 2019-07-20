#!/usr/bin/env python3
import sys, json, glob, os

per_line = """function {name}() {{
    echo "[+] Starting step {name}" >&2
    local TMP=$(mktemp -d)
    while read -r line
    do
        local TMP_FILE=$(mktemp -p $TMP)
        echo "[+] Running {command}" >&2
        {command}
    done
    cat $TMP/* | fzf ${{1:---filter=^}}
}}
"""

accepts_stdin = """function {name}() {{ 
    echo "[+] Starting step {name}" >&2
    local TMP_FILE=$(mktemp)
    {command} > $TMP_FILE
    cat $TMP_FILE | fzf ${{1:---filter=^}}
}}
"""

workflow_template = """{content}
function {name}() {{
    local TMP_DIR=$(mktemp -d)
    mkdir -p $TMP_DIR/background_tasks
    {background_tasks}
    {pipeline} | fzf ${{1:---filter=^}}
    rm -rf $TMP_DIR
}}

"""

wait_for_jobs="""function wait_for_jobs() {
    cat $1/background_tasks/* | fzf ${{2:---filter=^}}
}
"""

parallel_tasks_setup="""
    local INPUT=$(mktemp -p $TMP_DIR)
    cat <&0 > $INPUT
    """

def generate_step_function(step):
    template = accepts_stdin
    if "exec_per_line" in step and step["exec_per_line"]:
        template = per_line

    return template.format(**step)


source_function="""
function {name}() {{
    {command} | fzf ${{1:---filter=^}} 
}}
"""

def generate_source_function(source):
    return source_function.format(**source)


def generate_workflow_functions(data):
    workflow_name = data["name"]
   
    functions = []
    pipeline = []
    background_tasks = []
    for s in data["steps"]:
        if "command" in s:
            s["name"] = f"{workflow_name}_{s['name']}"
            functions.append(generate_step_function(s))

        if "parallel" in s and s["parallel"]:
            background_tasks.append(f"(cat $INPUT |{s['name']} > $(mktemp -p $TMP_DIR/background_tasks))")
        else:
            pipeline.append(s["name"])
   
    background_tasks_string = parallel_tasks_setup + " &\n    ".join(background_tasks)
    functions_string = "".join(functions)
    if len(background_tasks) > 0:
        background_tasks_string += " &\n    wait"
        pipeline.insert(0, "wait_for_jobs $TMP_DIR") 
    else:
        background_tasks_string = "# No background tasks"

    args = {"name": workflow_name, "pipeline": " | ".join(pipeline), "background_tasks": background_tasks_string, "content": functions_string}
    return workflow_template.format(**args)

def generate_functions(directory, generator_function):
    functions = []
    for f in glob.glob(os.path.join(directory, "*.json")):
        tmp = json.load(open(f))
        for data in tmp:
            functions.append(generator_function(data))

    return functions

time_trigger_template="""function trigger_{name}() {{
    {source} | {command} | {sink}
    sched +{repeat_freq} trigger_{name}
}}
sched {start_time} trigger_{name}

"""

fs_trigger_script="""function trigger_{name}() {{
    inotifywait -m -e close_write --format %f {path} | while read file_name
    do
        {pipeline}
    done
}}
trigger_{name} &
"""

trigger_script="""#!/usr/bin/env zsh
zmodload zsh/sched
source shell_functions.zsh

{content}
"""

def generate_trigger_function(trigger):
    if trigger["type"] == "time":
        return time_trigger_template.format(**trigger)
    
    if trigger["type"] == "fs_watch":
        pipeline = f"{trigger['command']} | {trigger['sink']}"
        if trigger["source"] != "":
            pipeline = f"{trigger['source']} | {pipeline}"

        trigger["pipeline"] = pipeline
        return fs_trigger_script.format(**trigger)

def generate_trigger_functions(dirs):
    functions = []

    for d in dirs:
        functions += generate_functions(os.path.join(d, "triggers"), generate_trigger_function)

    with open("triggers.zsh", "w") as script:
        c = trigger_script.format(content="".join(functions))
        script.write(c)

def generate_shell_functions(dirs):
    functions = []
    for d in dirs:
        functions += generate_functions(os.path.join(d, "sources"), generate_source_function)
        functions += generate_functions(os.path.join(d, "sinks"), generate_source_function)
        functions += generate_functions(os.path.join(d, "pipelines"), generate_workflow_functions)

    functions.insert(0, wait_for_jobs)

    with open("shell_functions.zsh", "w") as script:
        script.write(''.join(functions))

if __name__ == "__main__":
    dirs = [os.environ["BRIAN_HOME"], os.environ["PROJECT_DIR"]]

    generate_shell_functions(dirs)
    generate_trigger_functions(dirs)
    print("Generated all the required functions....")
    print("run 'source shell_functions.zsh' to load all sources/sinks/worklflows")
    print("run 'source triggers.zsh' to setup filewatchers and time based triggers")

