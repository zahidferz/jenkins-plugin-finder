import sys
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import zipfile
import os
import shutil
from packaging.version import Version
from packaging.version import parse as parse_version
import xml.etree.ElementTree as ET

## Desired jenkinsversion
jenkinsversion = Version(sys.argv[1])
## Empty list of pluginurls
pluginurls=[]
global pomfile, data

#$##$##$##$##$#
#$# Functions #
#$##$##$##$##$#

####################
## PLUGIN CHECKER ##
####################
def pluginchecker(pluginurlversion):
    # Download pluginurlversion extract it, and check if the value of the Jenkins-Version is desired compared with jenkinsversion
    ## Desired preffix for extract
    desiredpluginurlversions=[]
    pluginame = os.path.basename(pluginurlversion).split('.')[0]
    prefix =os.getcwd() + '/extract/' + pluginame + '/'
    os.mkdir(prefix)
    r = requests.get(pluginurlversion) # download the file
    with open(prefix + 'plugin.hpi', 'wb') as file: # save the file
        file.write(r.content)
    with zipfile.ZipFile(prefix + 'plugin.hpi', 'r') as file: # extract the file
        file.extractall(prefix)
    # open the MANIFEST
    manifest = open(prefix + "META-INF/MANIFEST.MF", "r")
    # iterate of each line in the MANIFEST
    for line in manifest.readlines():
        # look for the line with name 'Jenkins-Version'
        if 'Jenkins-Version' in line:
            # get the value after ':'
            value = line.split(": ")[1].strip()
            pluginjenkinsversion = Version(value)
            if pluginjenkinsversion <= jenkinsversion: # if the pluginjenkinsversion is equal or smaller than jenkinsversion append the pluginurlversion to the desiredpluginurlversions
                print(pluginurlversion)
                desiredpluginurlversions.append(pluginurlversion)
                # Close the MANIFEST
                manifest.close()
                # Find the POM 
                for root, dirs, files in os.walk(prefix):
	                for file in files:
	                	if file == 'pom.xml':
	                		data=open((os.path.join(root, file)), 'r').read()
                # Create the bsoup object of the data 
                Bs_data = BeautifulSoup(data, "xml")
                for dependency in Bs_data.find_all('dependency'):
                    if dependency.find('version') != None :
                        version = dependency.find('version').text
                        group = dependency.find('groupId').text
                        if '${' not in version:
                            if 'io.jenkins.plugins' in group or 'org.jenkins-ci.plugins' in group:
                                artifact = dependency.find('artifactId').text.strip()
                                version = dependency.find('version').text.strip()
                                generateurl = 'https://updates.jenkins.io//download/plugins/',artifact,'/',version,'/',artifact,'.hpi'
                                dependencyurl = ''.join(generateurl)
                                desiredpluginurlversions.append(dependencyurl)
                                print(dependencyurl)
                # Remove the extracted plugin
                shutil.rmtree(prefix)
            else:
                # Close the MANIFEST
                manifest.close()
                # Remove the extracted plugin
                shutil.rmtree(prefix)

    return desiredpluginurlversions

    # If the desired pluginurlversion has been found the for loop in search of the pluginurlversions will stop delivering the desiredpluginurlversion

####################
## latest_version ##
####################

def latest_version(urls):
  plugins = {}
  latest_plugins = {}
  latestdesiredplugins = []
  
  for url in urls:
    version_text = url.rsplit('/', 2)[1]
    name = os.path.basename(url).split('.')[0]
    if '.v' in version_text:
        version_parts = version_text.split('.')
        version_parts[-1] = '0'
        resulted_version = '.'.join(version_parts)
        version = parse_version(resulted_version.replace('-',''))
        plugins[url] = name, version
    else:
        version = parse_version(version_text.replace('-',''))
        plugins[url] = name, version
      
  for url, (plugin_name, version) in plugins.items():
      if plugin_name not in latest_plugins:
          latest_plugins[plugin_name] = (url, version)
      elif version > latest_plugins[plugin_name][1]:
          latest_plugins[plugin_name] = (url, version)


  for name, (url,version) in latest_plugins.items():
    latestdesiredplugins.append(url)
  
  return latestdesiredplugins
##########################
## PLUGIN URL VERSIONS ##
##########################
# Find their pluginurlversions and use pluginchecker to get the propper plugin whit the desiredpluginversions
def pluginurlversion(pluginurl):
    desiredpluginurlversions=[]
    res = requests.get(pluginurl).text
    soup = BeautifulSoup(res, 'html.parser')
    items = soup.find_all('a', attrs={"class":"version"})
    for each in items:
        link = each.get("href")
        if "latest" in link:
            pass
        else:
            pluginurlversion='https://updates.jenkins.io/'+link
            desiredpluginurlversions=pluginchecker(pluginurlversion)
            if  desiredpluginurlversions != []:
                break
    return desiredpluginurlversions

#$##$##$##$##$#
#$# Main #$##$#
#$##$##$##$##$#
if __name__ == '__main__':

    # Opening the file plugins.list and creating the pluginurls list of the plugins to fech their data
    with open('plugins.list', 'r') as f:
        plugins = [line.strip('\n') for line in f]
    for plugin in plugins:
        pluginurl='https://updates.jenkins.io/download/plugins/'+plugin
        pluginurls.append(pluginurl)
    
    desiredpluginurlversions=[]
    # For plugins
    # pool object with number of elements in the list
    pool = Pool(processes=len(pluginurls))
    pluginpool=(pool.map(pluginurlversion, pluginurls))
    for pluginlist in pluginpool:
        for plugin in pluginlist:
            desiredpluginurlversions.append(plugin)
    
    print("=======SUMMARY======")
    for plugin in latest_version(desiredpluginurlversions):
        print(plugin)





