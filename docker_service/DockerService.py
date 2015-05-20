#!/usr/bin/env python
#

import sys
from docker import Client
from optparse import OptionParser
import json
from zabbix.sender import ZabbixMetric, ZabbixSender

class DockerService(object):
    """Create an object for a Docker service. Assume it is stopped."""

    def __init__(self, url):

        self.url = url
        #self.container = container
        self.docker_running = False

    def list_containers(self):

        docker_conn_list = Client(base_url=self.url)

        try:
            containerlist = docker_conn_list.containers()
            self.docker_running = True
        # Apologies for the broad exception, it just works here.
        except Exception:
            self.docker_running = False

        #print containerlist

        if self.docker_running:
            # print 'status ok succeeded in obtaining docker container list
            return containerlist
            #for container in containerlist:
            #    print container['Id']

    def docker_stats(self, container):
        """Connect to the Docker object and get stats. Error out on failure."""

        docker_conn = Client(base_url=self.url)

        try:
            stats = docker_conn.stats(container)
            self.docker_running = True
        # Apologies for the broad exception, it just works here.
        except Exception:
            self.docker_running = False

        if self.docker_running:
            # print 'status ok succeeded in obtaining docker container stats.'
            for stat in stats:
                s = json.loads(stat)
                return s        
        else:
            print 'status err failed to obtain docker container stats.'
            sys.exit(1)

    def calculate_cpu_percent(self, previousCPU, previousSystem, container):
        cpuPercent = 0.0
        stats = self.docker_stats(container)
        cpuDelta = float(stats['cpu_stats']['cpu_usage']['total_usage']) - previousCPU
        systemDelta = float(stats['cpu_stats']['system_cpu_usage']) - previousSystem

        if systemDelta > 0.0 and cpuDelta > 0.0 :
                cpuPercent = round((cpuDelta / systemDelta) * float(len(stats['cpu_stats']['cpu_usage']['percpu_usage'])) * 100.0, 2)

        return cpuPercent

    def calculate_upercent_used_memory(self, container):

        stats = self.docker_stats(container)
        used_memory = stats['memory_stats']['usage']
        max_memory = stats['memory_stats']['limit']
        percent_used_memory = round(( float(used_memory) / max_memory ) * 100, 2)
        return percent_used_memory
