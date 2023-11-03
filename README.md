# Jenkins-plugin-finder
![jenkins](https://www.jenkins.io/images/logos/formal/formal.png)
This script will take the fisrt argument as the jenkins version desired , and will try to search the compatible plugins on the plugins.list.

## Requirements 
- Python 3.11.2

## Steps 
- Install dependencies
```shell
pip install -r requirements.txt
```
- Add the plugins you're looking into plugins.list on a list format with a plugin for each line
```shell
sshd
jquery3-api
git
```
- Execute the plugin_finder with the desired version
```shell
python plugin_finder.py 2.319.3
```
List of current plugins
https://updates.jenkins.io/current/update-center.actual.json