from docker_service import DockerService

parser = DockerService.OptionParser()
parser.add_option('-u', '--url', default='unix://var/run/docker.sock',
                  help='URL for Docker service (Unix or TCP socket).')
parser.add_option('-l', action="store_true", dest="list", default=False)
(opts, args) = parser.parse_args()

# Docker access
docker_service = DockerService.DockerService(opts.url)
containerslist = docker_service.list_containers()
if opts.list == True :
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
else :
    for container in containerslist:
        Name = container['Names']
        stats = docker_service.docker_stats(container['Id'])
        previousCPU = stats['cpu_stats']['cpu_usage']['total_usage']
        previousSystem = stats['cpu_stats']['system_cpu_usage']
        CPUPercent = docker_service.calculate_cpu_percent(previousCPU, previousSystem, container)
        PercentMemoryUsed = docker_service.calculate_upercent_used_memory(container)

        packet = [
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[cpu_used_percent]', round(CPUPercent, 2)),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[memory_used_percent]', PercentMemoryUsed),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[bytes_received]', stats['network']['rx_bytes']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[bytes_sent]', stats['network']['tx_bytes']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_received]', stats['network']['rx_packets']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[packets sent]', stats['network']['tx_packets']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_received_dropped]', stats['network']['rx_dropped']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_sent_dropped]', stats['network']['tx_dropped']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_received_erros]', stats['network']['rx_errors']),
             DockerService.ZabbixMetric(str(Name)[4:-2], 'user.docker[packets_sent_erros]', stats['network']['tx_errors']),
        ]

        result = DockerService.ZabbixSender(use_config=True).send(packet)
