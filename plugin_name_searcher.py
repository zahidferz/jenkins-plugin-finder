import json
from multiprocessing import Pool

global plugin

# Read our JSON into a variable
with open('jenkinsplugins.json') as json_file:
    jenkinsplugins = json.load(json_file)
# Opening the file plugins.list and creating the pluginurls list of the plugins to fech their data
with open('plugin.names', 'r') as f:
    pluginames = [line.strip('\n') for line in f]

def pluginsearcher(pluginame):
    print('------')
    print(pluginame)
    for plugin, plugindata in jenkinsplugins["plugins"].items():
        if pluginame in plugindata["title"]:
            print(plugindata['name'])
            return plugindata['name'], pluginame

if __name__ == '__main__':
    # pool object with number of elements in the list

    for p in pluginames:
        pluginsearcher(p)
    # pool = Pool(processes=len(pluginames))
    # pluginpool=(pool.map(pluginsearcher, pluginames))
