# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 12:42:13 2020

@author: Mikhaïl Bessa
"""
import datetime
import os
import statistics
import time

class HTTPTracker:
    
    def __init__(self, logfile="http.log"):
        self.interval = 10
        self.alarm_threshold = 10
        self.flow_rates = []
        self.reset_memory()
        self.alarm_triggered  = False
        with open(logfile, 'r') as self.file:
            print("Monitoring HTTP Traffic on {}: {}".format(logfile, os.linesep))
            last_update_time = time.time()
            for line in self.tail_logfile():
                if line != '':
                    self.update_state(line)
                t = time.time()
                if t - last_update_time > self.interval:
                    if len(self.flow_rates) > 11:
                        del self.flow_rates[0]
                    self.flow_rates.append(self.memory["hits"]*1.0/10)
                    self.print_state()
                    self.check_alarm()
                    self.reset_memory()
                    last_update_time = time.time()
                
    
    def tail_logfile(self):
            self.file.seek(0, os.SEEK_END)
            while True:
                line = self.file.readline()
                if not line:
                    time.sleep(0.1)
                    yield ''
                    continue
                yield self.split_line(line)
    
    def split_line(self, line):
        line = line.strip()
        tmp = line.split(' ', 3)
        remote_host, rfc, auth_user = tmp[0], tmp[1], tmp[2]
        tmp = tmp[3].split('"')
        request = tmp[1]
        tmp = tmp[2].split(' ')
        status, size = tmp[1], tmp[2]
        return remote_host, rfc, auth_user, request, status, size
    
    def print_state(self):
        print(datetime.datetime.now().strftime("Status at %H:%M:%S %z for the last ten seconds:"))
        print("hits per second: {}".format(
                self.memory["hits"]*1.0/10)
        )
        if self.memory['hits'] > 0:
            hosts = self.memory["users"]
            sorted_hosts = [(k, v) for k, v in sorted(hosts.items(), reverse=True, key=lambda x: x[1])]
            sorted_request_types =  [(k, v) for k, v in sorted(self.request_types.items(), reverse=True, key=lambda x: x[1])]
            sorted_sections = [(k, v) for k, v in sorted(self.sections.items(), reverse=True, key=lambda x: x[1])]
            print("remote hosts with most hits: {}".format(
                sorted_hosts[:min(5, len(sorted_hosts))]
            ))
            print("status: {}".format(self.memory["status"]))
            print("total size: {} bytes, average size: {} bytes".format(
                self.memory["total_size"],
                self.memory['total_size']*1.0/self.memory['hits']
            ))
            print("request types: {}".format(
                sorted_request_types[:min(5, len(sorted_request_types))]
            ))
            print("sections with most hits: {}".format(
                sorted_sections[:min(5, len(sorted_sections))]
            ))
        print()
    
    def update_state(self, l):
        remote_host, rfc, auth_user, request, status, size = l
        self.memory["hits"] += 1
        self.memory["total_size"] += int(size)e
        if self.memory["users"].get(remote_host, 0) > 0:
            self.memory["users"][remote_host] += 1 
        else:
            self.memory["users"][remote_host] = 1    
        if status[0] == '1':
            self.memory["status"]["info"] += 1
        elif status[0] == '2':
            self.memory["status"]["success"] += 1
        elif status[0] == '3':
            self.memory["status"]["client_error"] += 1
        elif status[0] == '4':
            self.memory["status"]["server_error"] += 1
        
        tmp = request.split(' ')
        request_type = tmp[0]
        tmp = tmp[1].split('/', 2)
        if len(tmp) > 0:
            section = tmp[1]
            if self.sections.get(section, 0) > 0:
                self.sections[section] += 1
            else:
                self.sections[section] = 1
        
        if self.request_types.get(request_type, 0) > 0:
                self.request_types[request_type] += 1
        else:
                self.request_types[request_type] = 1
        
    
    def check_alarm(self):
        mean_flow_rate = statistics.mean(self.flow_rates)
        if self.alarm_triggered:
            if mean_flow_rate < self.alarm_threshold:
                self.alarm_triggered = False
                print("The traffic is back to normal at {} {}".format(
                    self.current_time(),
                    os.linesep
                ))
        else:
            if mean_flow_rate > self.alarm_threshold:
                self.alarm_triggered = True
                print("High traffic generated an alert - hits = {}, triggered at {} {}".format(
                    mean_flow_rate, 
                    self.current_time(),
                    os.linesep
                ))
        
    def current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")
        
    def reset_memory(self):
        self.request_types, self.sections = {}, {}
        self.memory = {
            "sections": {},
            "users": {},
            "hits": 0,
            "total_size": 0,
            "status":{"success": 0, "info":0, "redirection":0, "client_error":0, "server_error":0}
        }

            
            
x = HTTPTracker()
    
    

            
    