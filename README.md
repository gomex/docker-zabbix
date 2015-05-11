# Goal

Monitor resource used by running containers

# TODO

- [x] Get informations about percent used CPU, percent used RAM memory and network 
- [x] Add options to get information from all containers and not only using id container
- [ ] Create zabbix module

# Requirements

## docker-py library 

``` 
# pip install docker-py
```

or
```
# git clone git@github.com:docker/docker-py.git
# cd docker-py
# python setup.py install
```

## py-zabbix library 

```
# pip install py-zabbix
```
or

```
# git clone git@github.com:blacked/py-zabbix.git
# cd py-zabbix
# python setup.py install
```

## Packages used

* python 2.7.9
* docker 1.6
* zabbix agent and server 2.4

# Initial Configuration

## Docker host server

```
# git clone git@gitlab.com:Gomex/docker-monitor.git
# cd docker-monitor
# cp *.py /etc/zabbix
# chowm -R zabbix /etc/zabbix/
# chmod u+x /etc/zabbix/*.py
# echo "zabbix ALL=NOPASSWD: /etc/zabbix/list_containers_docker_lld.py" >> /etc/sudoers
# echo "*/5 * * * *   root /etc/zabbix/docker_stats.py" > /etc/cron.d/docker-zabbix
# apt-get install zabbix-agent
# echo "EnableRemoteCommands=1" >> /etc/zabbix/zabbix_agentd.conf
# /etc/init.d/zabbix-agent restart
```

## Zabbix server

1. Import that [template](https://gitlab.com/Gomex/docker-monitor/raw/master/zbx_export_templates.xml) 
1. Create a host to your Docker host server and link the template "Template Docker Host"
1. Wait the containers :P

## If you don't have a zabbix server to test

```
# docker pull berngp/docker-zabbix
# docker run -d -P berngp/docker-zabbix
```

Check which port was mapped to tcp/80

``` 
# docker ps | grep "docker-zabbix"
```

# Inspiration

I decided create this solution after read that [news](http://www.rackspace.com/blog/addressing-hybrid-architecture-complexity-with-new-docker-monitoring-plugin/) and used part of code to start my own.
