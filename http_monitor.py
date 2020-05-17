# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 12:42:13 2020

@author: Mikhaïl Bessa
"""
from collections import defaultdict
from datetime import timedelta, datetime, timezone

import argparse
import os
import sys
import time

class HTTPMonitor:
    
    def __init__(self, logfile="http.log", interval=10, alarm_threshold=10, verbosity=True, duration=None, stdout=sys.stdout):
        self.interval = interval
        self.alarm_threshold = alarm_threshold
        self.alarm_triggered  = False
        self.logfile = logfile
        self.stdout = stdout
        self.verbosity = verbosity
        self.duration = duration
        self.cum_flow_rates = [0.0]

 
    def start(self):
        with open(self.logfile, 'r') as self.file:
            self.reset_memory()
            initial_time = datetime.now(tz=timezone.utc)
            last_update_time, timestamp, pause = initial_time, initial_time , False
            
            if self.verbosity:
                self.stdout.write("Monitoring HTTP logs on {}, from {}...\n".format(
                        self.logfile, 
                        timestamp.strftime("%H:%M:%S")
                ))
                
            for line in tail(self.file):
                if line != '':
                    timestamp = self.register_line(line)
                    if pause:
                        print(timestamp, "----", last_update_time, "\n")
                        pause = False
                    if (timestamp - last_update_time).total_seconds() >= self.interval:
                        self.update_status(timestamp)
                        last_update_time = timestamp
                
                elif self.interval - (datetime.now(tz=timezone.utc) - timestamp).total_seconds() < -0.5:
                    timestamp = last_update_time + timedelta(seconds=self.interval)
                    self.update_status(timestamp)
                    last_update_time = timestamp
                    pause = True
                    
                if self.duration and (timestamp - initial_time).total_seconds() >= self.duration:
                    return 
                    
            self.stdout.write("Done Monitoring.")
    
    
    def split_line(self, line): # parse HTTP request
        tmp = line.strip().split(' ', 3)
        remote_host, rfc, auth_user = tmp[0], tmp[1], tmp[2]
        tmp = tmp[3].split('"')
        timestamp = tmp[0].strip()
        request = tmp[1]
        tmp = tmp[2].split(' ')
        status, size = tmp[1], int(tmp[2])
        
        tmp = request.split(' ')
        request_type = tmp[0]
        tmp = tmp[1].split('/', 2)
        section = tmp[1] if len(tmp) > 0 else ''
        return remote_host, rfc, auth_user, timestamp, request_type, section, status, size
    
    def update_status(self, timestamp): 
        if len(self.cum_flow_rates) > 12:
            self.cum_flow_rates[-1] += self.cum_flow_rates[0] - self.cum_flow_rates[1]
            del self.cum_flow_rates[0]
        cum_flow_rate = self.cum_flow_rates[-1] + self.memory["hits"] / self.interval
        self.cum_flow_rates.append(cum_flow_rate)
        print(self.cum_flow_rates)
        if self.verbosity:
            self.print_state(timestamp)
        self.check_alarm(timestamp)
        self.reset_memory()
        
    
    def print_state(self, timestamp):
        self.stdout.write(timestamp.strftime("Status at: [%d/%b/%Y:%H:%M:%S %z]\n"))
        self.stdout.write("hits per second: {} \n".format(
                self.memory["hits"]/self.interval)
        )
        if self.memory['hits'] > 0:
            hosts = self.memory["users"]
            sorted_hosts = [(k, v) for k, v in sorted(hosts.items(), reverse=True, key=lambda x: x[1])]
            sorted_request_types =  [(k, v) for k, v in sorted(self.request_types.items(), reverse=True, key=lambda x: x[1])]
            sorted_sections = [(k, v) for k, v in sorted(self.sections.items(), reverse=True, key=lambda x: x[1])]
            self.stdout.write("remote hosts with most hits: {}\n".format(
                sorted_hosts[:min(5, len(sorted_hosts))]
            ))
            self.stdout.write("status: {}\n".format(self.memory["status"]))
            self.stdout.write("total size: {} bytes, average size: {} bytes\n".format(
                self.memory["total_size"],
                round(self.memory['total_size']*1.0/self.memory['hits'], 2)
            ))
            self.stdout.write("request types: {}\n".format(
                sorted_request_types[:min(5, len(sorted_request_types))]
            ))
            self.stdout.write("sections with most hits: {}\n".format(
                sorted_sections[:min(5, len(sorted_sections))]
            ))
        self.stdout.write("\n")
    
    def register_line(self, l):
        try:
            remote_host, rfc, auth_user, timestamp, request_type, section, status, size = self.split_line(l)
            self.memory["hits"] += 1
            self.memory["total_size"] += size
            self.memory["users"][remote_host] += 1 
            self.sections[section] += 1
            self.request_types[request_type] += 1

            if status[0] == '1':
                self.memory["status"]["info"] += 1
            elif status[0] == '2':
                self.memory["status"]["success"] += 1
            elif status[0] == '3':
                self.memory["status"]["client_error"] += 1
            elif status[0] == '4':
                self.memory["status"]["server_error"] += 1
                
            timestamp = datetime.strptime(timestamp, "[%d/%b/%Y:%H:%M:%S %z]")
            return timestamp
        except:
            self.stdout.write("[WARNING] Skipped log line with wrong format \n")
            return datetime.now(tz=timezone.utc)
        
    
    def check_alarm(self, timestamp):
        mean_flow_rate = self.cum_flow_rates[-1] / (len(self.cum_flow_rates) - 1)
        print(mean_flow_rate)
        if self.alarm_triggered:
            if mean_flow_rate < self.alarm_threshold:
                self.alarm_triggered = False
                if self.verbosity:
                    self.stdout.write("The traffic is back to normal at {}\n\n".format(
                        timestamp
                    ))
        else:
            if mean_flow_rate > self.alarm_threshold:
                self.alarm_triggered = True
                if self.verbosity:
                    self.stdout.write("High traffic generated an alert - hits = {:.2f}, triggered at {}\n\n".format(
                        mean_flow_rate, 
                        timestamp
                    ))
        
    def current_time(self):
        return datetime.now().strftime("%H:%M:%S")
        
    def reset_memory(self):
        self.request_types, self.sections = defaultdict(lambda: 0), defaultdict(lambda: 0)
        self.memory = {
            "sections": defaultdict(lambda: 0),
            "users": defaultdict(lambda: 0),
            "hits": 0,
            "total_size": 0,
            "status":{"success": 0, "info":0, "redirection":0, "client_error":0, "server_error":0}
        }


def tail(stdout):
            stdout.seek(0, os.SEEK_END)
            while True:
                line = stdout.readline()
                if not line:
                    time.sleep(0.1)
                    yield ''
                    continue
                yield line

            
if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-f', "--filename", type=str, help='logfile path', default="test.log")
    parser.add_argument('-t', "--threshold", type=int, default=10, help='Alarm threshold')
    parser.add_argument('-v', "--verbosity", action="store_true", help='')

    args = parser.parse_args()          
    x = HTTPMonitor(logfile=args.filename, alarm_threshold=args.threshold, verbosity=args.verbosity)
    x.start()
    
    

            
    