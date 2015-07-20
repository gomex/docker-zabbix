#!/usr/bin/env python
#

from docker_service import DockerService

parser = DockerService.OptionParser()
parser.add_option('-u', '--url', default='unix://var/run/docker.sock',
                  help='URL for Docker service (Unix or TCP socket).')
parser.add_option('-l', action="store_true", dest="list", default=False)
(opts, args) = parser.parse_args()

# Docker access
docker_service = DockerService.DockerService(opts.url)
containerslist = docker_service.list_containers()
if opts.list:
    import json
    con_list = []
    ## TODO: implement None return handle
    for container in containerslist:
        Name = container['Names']
        con_list.append({'{#NAME}': str(Name)[4:-2]})
    con_dict = {}
    con_dict['data'] = con_list
    print(json.dumps(con_dict))
else:
    for container in containerslist:
        Name = container['Names']
        Name = str(Name)[4:-2]
        stats = docker_service.docker_stats(container['Id'])
        prevCPU = stats['cpu_stats']['cpu_usage']['total_usage']
        prevSystem = stats['cpu_stats']['system_cpu_usage']
        CPUPerc = docker_service.calc_cpu_perc(prevCPU, prevSystem, container)
        PercMemUsed = docker_service.calc_upercent_used_memory(container)
        key_cpu_used = 'user.docker[cpu_used_percent]'
        key_mem_used = 'user.docker[memory_used_percent]'
        key_bytes_rec = 'user.docker[bytes_received]'
        key_bytes_sent = 'user.docker[bytes_sent]'
        key_pkt_rec = 'user.docker[packets_received]'
        key_pkt_sent = 'user.docker[packets sent]'
        key_pkt_rec_drop = 'user.docker[packets_received_dropped]'
        key_pkt_sent_drop = 'user.docker[packets_sent_dropped]'
        key_pkt_rec_err = 'user.docker[packets_received_erros]'
        key_pkt_sent_err = 'user.docker[packets_sent_erros]'

        rx_bytes = stats['network']['rx_bytes']
        tx_bytes = stats['network']['tx_bytes']
        rx_packets = stats['network']['rx_packets']
        tx_packets = stats['network']['tx_packets']
        rx_dropped = stats['network']['rx_dropped']
        tx_dropped = stats['network']['tx_dropped']
        rx_errors = stats['network']['rx_errors']
        tx_errors = stats['network']['tx_errors']

        ## Debug 
        #print(stats)

        packet = [
          DockerService.ZabbixMetric(Name, key_cpu_used, round(CPUPerc, 2)),
          DockerService.ZabbixMetric(Name, key_mem_used, PercMemUsed),
          DockerService.ZabbixMetric(Name, key_bytes_rec, rx_bytes),
          DockerService.ZabbixMetric(Name, key_bytes_sent, tx_bytes),
          DockerService.ZabbixMetric(Name, key_pkt_rec, rx_packets),
          DockerService.ZabbixMetric(Name, key_pkt_sent, tx_packets),
          DockerService.ZabbixMetric(Name, key_pkt_rec_drop, rx_dropped),
          DockerService.ZabbixMetric(Name, key_pkt_sent_drop, tx_dropped),
          DockerService.ZabbixMetric(Name, key_pkt_rec_err, rx_errors),
          DockerService.ZabbixMetric(Name, key_pkt_sent_err, tx_errors),
        ]

        result = DockerService.ZabbixSender(use_config=True).send(packet)
