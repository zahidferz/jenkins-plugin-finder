import sys
import requests
from bs4 import BeautifulSoup
import requests
import zipfile
import os
import shutil
from packaging.version import Version

## Desired jenkinsversion
jenkinsversion = Version(sys.argv[1])
## Empty list of pluginurls
pluginurls=[]
## Empty list of desiredpluginurlversions
desiredpluginurlversions=[]
## Desired preffix for extract
prefix = 'extract/'


#$##$##$##$##$#
#$# Functions #
#$##$##$##$##$#

####################
## PLUGIN CHECKER ##
####################
def pluginchecker(pluginurlversion):
    # Download pluginurlversion extract it, and check if the value of the Jenkins-Version is desired compared with jenkinsversion
    os.mkdir(prefix)
    r = requests.get(pluginurlversion) # download the file
    with open(prefix + 'plugin.hpi', 'wb') as file: # save the file
        file.write(r.content)
    with zipfile.ZipFile(prefix + 'plugin.hpi', 'r') as file: # extract the file
        file.extractall(prefix)
    # open the MANIFEST
    manifest = open("extract/META-INF/MANIFEST.MF", "r")
    # iterate of each line in the MANIFEST
    for line in manifest.readlines():
        # look for the line with name 'Jenkins-Version'
        if 'Jenkins-Version' in line:
            # get the value after ':'
            value = line.split(": ")[1].strip()
            pluginjenkinsversion = Version(value)
            if pluginjenkinsversion <= jenkinsversion: # if the pluginjenkinsversion is equal or smaller than jenkinsversion append the pluginurlversion to the desiredpluginurlversions
                desiredpluginurlversions.append(pluginurlversion)
                # Close the MANIFEST
                manifest.close()
                # Remove the extracted plugin
                shutil.rmtree(prefix)
                return pluginurlversion
            else:
                # Close the MANIFEST
                manifest.close()
                # Remove the extracted plugin
                shutil.rmtree(prefix)
                return ""
    # If the desired pluginurlversion has been found the for loop in search of the pluginurlversions will stop delivering the desiredpluginurlversion

#$##$##$##$##$#
#$# Main #$##$#
#$##$##$##$##$#

#################
## PLUGIN URLS ##
#################
# Opening the file plugins.list and creating the pluginurls list of the plugins to fech their data
with open('plugins.list', 'r') as f:
    plugins = [line.strip('\n') for line in f]
for plugin in plugins:
    pluginurl='https://updates.jenkins.io/download/plugins/'+plugin
    pluginurls.append(pluginurl)


##########################
## PLUGIN URL VERSIONS ##
##########################
# For each plugin url find their pluginurlversions
for pluginurl in pluginurls:
    res = requests.get(pluginurl).text
    soup = BeautifulSoup(res, 'html.parser')
    items = soup.find_all('a', attrs={"class":"version"})
    for each in items:
        link = each.get("href")
        if "latest" in link:
            pass
        else:
            pluginurlversion='https://updates.jenkins.io/'+link
        # Check if the plugin is compatible with the jenkinsversion
            if pluginchecker(pluginurlversion) != "":
                print(pluginurlversion)
                break







