#!/bin/python

import winerror
import win32serviceutil
import win32service
import win32event
import os
import sys
import time
from util import track_processes

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'ProcessTrackerService'
    _svc_display_name_ = 'Process Tracker Service'
    _svc_reg_class = "tmp.reg_class"
    _svc_description_ = "tmp description"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.Stop = False
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        while self.run:
            track_processes()
            time.sleep(300)  # Sleep for 5 minutes