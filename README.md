# brian
Automate stuff and build cool piplines and trigger things

Basically just creates zsh functions that operate on stdin and pipe to stdout.
Main use for automating bugbounty recon stuff but can be anything really

```
$ git clone https://github.com/bad-hombres/brian.git
```
Remeber to create symlinks to all your tools in the $BRIAN_HOME/tools

# Tools used
https://github.com/rockymadden/slack-cli
https://github.com/OJ/gobuster
https://github.com/aboul3la/Sublist3r
https://github.com/tomnomnom/hacks/tree/master/assetfinder
https://github.com/junegunn/fzf

inotify-tools
zsh (and zsh/sched plugin)

# How to use
```
$ mkdir /path/to/empty/project/dir
$ cd /path/to/project/dir
$ cat <<EOF > project.zsh
export PROJECT_NAME=my_project
export BRIAN_HOME=/path/to/brian

source $BRIAN_HOME/brian_general.zsh
source shell_functions.zsh
EOF
$ source project.zsh
$ echo somedomain.com > domains.txt
```
Start using: eg

```
$ domains | subdomains | new_subdomain_file
```
for every line in the domains .txt run sublist3r, assetfinder, gobuster in
parallel then sort and dedup them and then output that to a file in the
subdomains dir named based on the datetime

```
$ newest_subdomains | slack new_subdomains.txt "#brian"
```

This will diff the new list of subdomains against all previously enumerated
subdomains and upload the new domains to the #brian channel in slack as a file
named new_subdomains

Oh yeah triggers!!! 
In new windows (every one uses tmux right?)
```
$ source triggers.zsh
```
These allow you to run stuff when files / directories are written to or time
based. See the example json files provided

if you create json files in the project created sources, sinks, pipelines,
triggers directories then they will be included along with with ones provided
with brian so you may want to think about name clashes

# Todo?
- Better docs.
- Build more stuff with it (its all zsh in the end)
