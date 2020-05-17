# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 18:02:48 2020

@author: Mikhaïl Bessa
"""

import datetime
import time
import argparse

from random import getrandbits, choice, randint
from ipaddress import IPv4Address



class LogGenerator:
    
    def __init__(self, filename):
        self.auth_users = ["july", "violet", 
            "rose", "ava", "mariam", "mark",
            "samy", "samuel", "mikhaïl", "farah", "daniel", "jules"]
        self.requests = ["POST", "GET", "PUT", "DELETE", "OPTIONS"]
        self.sections = ["/", "/posts", "/api", "/api/test", "api/home", "/contact", "/about/author", "/about/project"]
        self.ips = [self.generate_ip() for i in range(10)]
        self.filename = filename
    
    def generate_logs(self, duration=10, interval=0.05):
        with open(self.filename, "a") as f:
            t = time.time()
            initial_time = t
            while t - initial_time < duration:
                f.write(self.generate_line()) # write http log line
                time.sleep(interval) # pause before next line
                t = time.time()
            
    def generate_line(self):
        auth_user = choice(self.auth_users)
        current_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("[%d/%b/%Y:%H:%M:%S %z]")
        request = choice(self.requests) + ' ' + choice(self.sections)
        status = randint(100, 500)
        size = randint(1, 999)
        line = '{} {} {} {} "{}" {} {}\n'.format(
            choice(self.ips), 
            "-", 
            auth_user, 
            current_time, 
            request, 
            status, 
            size        
        )
        return line

    def generate_ip(self):
        bits = getrandbits(32) # generates an integer with 32 random bits
        return  str(IPv4Address(bits)) # instances an IPv4Address object from those bits
   

if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-f', "--filename", type=str, help='logfile path', default="test.log")
    parser.add_argument('-d', "--duration", type=int, default=30, help='')
    parser.add_argument('-i', "--interval", type=int, default=0.05, help='')

    args = parser.parse_args()
    LG = LogGenerator(args.filename)
    LG.generate_logs(duration=args.duration, interval=args.interval)
