#!/usr/bin/env python
#
from docker import Client
from optparse import OptionParser
import json

class DockerService(object):

    def __init__(self, url):

        self.url = url
        self.docker_running = False

    def list_containers(self):

        docker_conn_list = Client(base_url=self.url)

        try:
            containerlist = docker_conn_list.containers()
            self.docker_running = True
        except Exception:
            self.docker_running = False

        if self.docker_running:
            return containerlist

def main():

    parser = OptionParser()
    parser.add_option('-u', '--url', default='unix://var/run/docker.sock',
                      help='URL for Docker service (Unix or TCP socket).')
    (opts, args) = parser.parse_args() 

    docker_service = DockerService(opts.url)
    containerslist = docker_service.list_containers()

    first = 1;
    print "{\n";
    print "\t\"data\":[\n";

    for container in containerslist:

        if first == 0:
            print ",\n"
        first = 0
        Name = container['Names']
        #print "\t{",  "\"{#CONTAINERID}\":\"",container['Id'],"\",","\"{#name}\":\"",container['Id'],"\"}"
        print "\t{",  "\"{#NAME}\":\"",str(Name)[4:-2],"\"}"

    print "\n\t]\n"
    print "}\n"

if __name__ == '__main__':
    main()    
