# HTTP Traffic Monitor

## Requirements

python 3.7 and - standard library only

## Usage

### log_generator.py
This file contains a class, LogGenerator, that writes random http logs on a given log file, at a given frequency for a given duration

Initialization:
* logfile: log file path (default: '/tmp/access.log')

Then, the start() method takes two args
* duration: duration (in seconds, default: 30)
* interval: time interval between two successive writes (in seconds, default: 0.1)

This file can be used as a script too, with the following args:
* -f : log file path (default: '/tmp/aclaunchescess.log')
* -d : duration (in seconds, default: 30)
* -i : time interval between two successive writes (in seconds, default: 0.1)


### http_monitor.py
This file contains a class, HTTPMonitor, that monitors http traffic by reading a given log file,
display stats every 10 seconds and an alert if the average http traffic over the last two minutes 
is above a given threshold (the alarm check is done every 10s, after displaying the stats)

Initialization:
* logfile: log file path (default: '/tmp/access.log')
* alarm_threshold: alarm threshold (in requests per seconds, default: 10)
* duration: duration (in seconds, default: None)
* verbosity (default: True)

Then the start() method launches the monitoring.

This file can be used as a script too, with the following args:
* -f : log file path (default: '/tmp/access.log')
* -t : alarm threshold (in requests per seconds, default: 10)
* -v: print messages or not (default: False)

### test_http_monitor.py

This file contains a set of 8 tests for the HTTPMonitor class (unittest library). 
As a script, it runs all tests. All tests launch a HTTPMonitor (as a Thread or as a process) 
that monitors the mock log file test.log, and some launch a LogGenerator (as a process) that logs mock HTTP requests
on the same log file.

The tests are divided into 2 categories:
* the test_{} test the HTTPMonitor internal variables
* the test_output_{} test the HTTPMonitor's output
