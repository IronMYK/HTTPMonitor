# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:23:01 2020

@author: Mikhaïl Bessa
"""

import time

from threading import Thread
from multiprocessing import Process
from LogGenerator import LogGenerator
from HTTPMonitor import HTTPMonitor
from unittest import TestCase, main


class TestHTTPMonitor(TestCase): 
    
    def test_no_traffic(self):
        monitor = HTTPMonitor(verbosity=False, duration=30)
        p = Thread(target=monitor.start, daemon=True)
        p.start()
        time.sleep(15)
        assert(not monitor.alarm_triggered) #check if the alarm was triggered
        assert(monitor.flow_rates[-1] == 0)
        p.join()
    
    def test_normal_traffic(self):
        monitor = HTTPMonitor(verbosity=False, duration=30)
        generator = LogGenerator("http.log")
        p = Thread(target=monitor.start, daemon=True)
        p2 = Process(target=generator.generate_logs, kwargs={"duration":30, "interval": 0.12}, daemon=True)
        p2.start()
        p.start()
        while p.is_alive():
            if len(monitor.flow_rates) > 0:
                assert(not monitor.alarm_triggered) #check if the alarm was triggered
            time.sleep(1)
        p2.terminate()
    
    def test_high_traffic(self):
        monitor = HTTPMonitor(verbosity=False, duration=30)
        generator = LogGenerator("http.log")
        p = Thread(target=monitor.start)
        p2 = Process(target=generator.generate_logs, kwargs={"duration":40, "interval": 0.08}, daemon=True)
        p2.start()
        p.start()
        while p.is_alive():
            if len(monitor.flow_rates) > 0:
                assert(monitor.alarm_triggered) #check if the alarm was triggered
            time.sleep(1)
        p2.terminate()
        
    def test_alarm(self):
        monitor = HTTPMonitor(verbosity=False, duration=30)
        generator = LogGenerator("http.log")
        p = Thread(target=monitor.start, daemon=True)
        p2 = Process(target=generator.generate_logs, kwargs={"duration":10, "interval":0.05}, daemon=True)
        p2.start()
        p.start()
        time.sleep(15)
        assert(monitor.alarm_triggered) #check if the alarm was triggered
        p.join()
        self.assertFalse(monitor.alarm_triggered) #check if http traffic is back to normal
        p2.terminate()
    
    def test_http_monitor(self):
        monitor = HTTPMonitor(verbosity=False, duration=50)
        generator = LogGenerator("http.log")
        p = Thread(target=monitor.start, daemon=True)
        p2 = Process(target=generator.generate_logs, kwargs={"duration":20, "interval": 0.05}, daemon=True)
        p.start()
        time.sleep(12)
        p2.start()
        time.sleep(25)
        assert(monitor.alarm_triggered) #check if the alarm was triggered
        p.join()
        self.assertFalse(monitor.alarm_triggered) #check if http traffic is back to normal
        p2.terminate()
        
        
if __name__ == '__main__':
        main()