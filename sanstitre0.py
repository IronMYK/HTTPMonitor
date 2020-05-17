# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 18:02:48 2020

@author: Mikhaïl Bessa
"""

import datetime
import logging
import os
import time

from random import getrandbits, choice, randint
from ipaddress import IPv4Address



class LogGenerator:
    
    def __init__(self, filename):
        self.auth_users = ["july", "violet", 
            "rose", "ava", "mariam", "mark",
            "frank", "samuel", "mikhaïl"]
        self.requests = ["POST", "GET", "PUT", "DELETE", "OPTIONS"]
        self.sections = ["/posts", "/api", "/api/test", "api/home", "/contact", "/about/author", "/about/project"]
        self.ips = [self.generate_ip() for i in range(10)]
        logging.basicConfig(
            format='%(message)s',
            filename=filename
        )
    
    def generate_logs(self):
        for i in range(4000):
            logging.warning(self.generate_line())
            time.sleep(0.05)
            
    def generate_line(self):
        auth_user = choice(self.auth_users)
        current_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("[%d/%b:%H:%M:%S %z]")
        request = choice(self.requests) + ' ' + choice(self.sections)
        status = randint(100, 500)
        size = randint(1, 999)
        line = '{} {} {} {} "{}" {} {}'.format(
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
    
LG = LogGenerator("http.log")
LG.generate_logs()
