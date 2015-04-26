#!/usr/bin/env python
#

import sys
from docker import Client
from optparse import OptionParser
import json
from zabbix.api import ZabbixAPI
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

    def calculateCPUPercent(self, previousCPU, previousSystem, container):
        cpuPercent = 0.0
        stats = self.docker_stats(container)
        cpuDelta = float(stats['cpu_stats']['cpu_usage']['total_usage']) - previousCPU
        systemDelta = float(stats['cpu_stats']['system_cpu_usage']) - previousSystem

        if systemDelta > 0.0 and cpuDelta > 0.0 :
                cpuPercent = round((cpuDelta / systemDelta) * float(len(stats['cpu_stats']['cpu_usage']['percpu_usage'])) * 100.0, 2)

        return cpuPercent

    def calculateupercentusedmemory(self, container):

        stats = self.docker_stats(container)
        used_memory = stats['memory_stats']['usage']
        max_memory = stats['memory_stats']['limit']
        percent_used_memory = round(( float(used_memory) / max_memory ) * 100, 2)
        return percent_used_memory

def main():
    """Instantiate a DockerStats object and collect stats."""

    parser = OptionParser()
    parser.add_option('-u', '--url', default='unix://var/run/docker.sock',
                      help='URL for Docker service (Unix or TCP socket).')
    (opts, args) = parser.parse_args()
    
    # Docker access
    docker_service = DockerService(opts.url)
    containerslist = docker_service.list_containers()
    for container in containerslist:
        Name = container['Names']
        stats = docker_service.docker_stats(container['Id'])
        previousCPU = stats['cpu_stats']['cpu_usage']['total_usage']
        previousSystem = stats['cpu_stats']['system_cpu_usage']
        CPUPercent = docker_service.calculateCPUPercent(previousCPU, previousSystem, container)
        #print container['Names'], ' - CPU percent used:', round(CPUPercent, 2),'%' 
        PercentMemoryUsed = docker_service.calculateupercentusedmemory(container)

        packet = [
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[cpu_used_percent]', round(CPUPercent, 2)),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[memory_used_percent]', PercentMemoryUsed),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[bytes_received]', stats['network']['rx_bytes']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[bytes_sent]', stats['network']['tx_bytes']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_received]', stats['network']['rx_packets']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[packets sent]', stats['network']['tx_packets']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_received_dropped]', stats['network']['rx_dropped']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_sent_dropped]', stats['network']['tx_dropped']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_received_erros]', stats['network']['rx_errors']),
                 ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_sent_erros]', stats['network']['tx_errors']),
        ]

        result = ZabbixSender(use_config=True).send(packet)

        #print container['Names'], ' - Memory percent used:', PercentMemoryUsed, '%'
        #print container['Names'], ' - Bytes received from network:', stats['network']['rx_bytes']
        #print container['Names'], ' - Bytes sent to network:', stats['network']['tx_bytes']
        #print container['Names'], ' - Packets received from network:', stats['network']['rx_packets']
        #print container['Names'], ' - Packets sent to network:', stats['network']['tx_packets']
        #print container['Names'], ' - Packets received from network, but dropped:', stats['network']['rx_dropped']
        #print container['Names'], ' - Packets sent to network, but dropped:', stats['network']['tx_dropped']
        #print container['Names'], ' - Packets received from network, but with erros:', stats['network']['rx_errors']
        #print container['Names'], ' - Packets sent to network, but with erros:', stats['network']['tx_errors']

if __name__ == '__main__':
    main()
