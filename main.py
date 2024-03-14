#!/bin/python

import servicemanager
import winerror
import win32event
import win32service
import win32serviceutil
import win32gui
import os, sys, site
from sys import modules
from os.path import splitext, abspath
from util import track_processes, display_statistics, calculate_statistics, parse_logs
from app_service import AppService
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def init_service():
    try:
        print(f"Installing service {AppService._svc_name_}...")
        
        try:
            module_path = modules[AppService.__module__].__file__
        except AttributeError:
            # maybe py2exe went by
            from sys import executable
            module_path = executable
        
        module_file = splitext(abspath(module_path))[0]
        AppService._svc_reg_class = '%s.%s' % (module_file, AppService.__name__)

        win32serviceutil.InstallService(
            AppService._svc_reg_class,
            AppService._svc_name_,
            AppService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START
        )
        print(f"Service {AppService._svc_name_} installed.")
      
    except win32service.error as e:
        if e[0] == winerror.ERROR_SERVICE_EXISTS:
            pass # ignore install error if service is already installed

        else:
            raise

def install_service():
    try:
        # Check if service is already installed
        status = win32serviceutil.QueryServiceStatus(AppService._svc_name_)
        print(f"Service {AppService._svc_name_} is already installed.")
        stop_service()
        remove_service()                
    except Exception as e:
        pass
        
    init_service()
    start_service()

def start_service():
    try:
        win32serviceutil.StartService(AppService._svc_name_)
    except win32service.error as e:
        if ((e[0] == winerror.ERROR_SERVICE_ALREADY_RUNNING) or (e[0] == winerror.ERROR_ALREADY_RUNNING_LKG)):
            pass # ignore failed start if the service is already running

        elif (e[0] == winerror.ERROR_SERVICE_DOES_NOT_EXIST):
            # if the service is not installed, install it and try again
            init_service()
            win32serviceutil.StartService(AppService._svc_name_)

        else:
            # reraise any other start expection
            raise

        status = win32serviceutil.QueryServiceStatus(AppService._svc_name_)
        print("Service status: {}".format(status[1]))
        
def stop_service():
    try:
        win32serviceutil.StopService(AppService._svc_name_)
        print(f"Service {AppService._svc_name_} stopped.")
    except Exception as e:
        print(f"Error stopping service: {e}")

def remove_service():
    try:
        print("Stopping service...")
        stop_service()
    except Exception as e:
        print(f"Error stopping service: {e}")
        
    try:
        win32serviceutil.RemoveService(AppService._svc_name_)
        print(f"Service {AppService._svc_name_} removed.")
    except Exception as e:
        print(f"Error removing service: {e}")
           
def run_test_mode():
    
    print("Running in test mode...")
    track_processes()
    print("Processes tracked.")
    display_statistics()
    print("Statistics displayed.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'test':
            run_test_mode()
        elif sys.argv[1].lower() == 'stop':
            stop_service()
        elif sys.argv[1].lower() == 'start':
            start_service()
        elif sys.argv[1].lower() == 'remove':
            remove_service()
        elif sys.argv[1].lower() == 'stats':
            display_statistics()
        elif sys.argv[1].lower() == 'install':
            install_service()
        else:
            win32serviceutil.HandleCommandLine(AppService)
    else:
        win32serviceutil.HandleCommandLine(AppService)
