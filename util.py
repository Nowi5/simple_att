import psutil
import datetime
import time
import os
import glob
import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


att_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'att_data')
if not os.path.exists(att_data_folder):
    os.makedirs(att_data_folder)

att_blacklist = None

def get_blacklist():
    global att_blacklist
    if att_blacklist is None:
        blacklist_file = os.path.join(att_data_folder, "blacklist.txt")
        print(f'Openeing blacklist: {blacklist_file}')
        with open(blacklist_file, 'r') as file:
            att_blacklist = [line.strip().lower() for line in file]
            # print("Blacklist:")
            # print(att_blacklist)
    return att_blacklist

def track_processes():
    current_blacklist = get_blacklist()
    current_user = os.getlogin()
    current_time = datetime.now()
    active_processes = set()
    filename = os.path.join(att_data_folder, datetime.now().strftime("%Y-%m-%d") + ".csv")
    process_data = {}
    process_list = psutil.process_iter(['pid', 'name', 'create_time', 'username', 'exe'])

    # Check if the file exists and has the correct header
    if os.path.exists(filename):
        with open(filename, "r", newline='') as file:
            csv_reader = csv.DictReader(file)
            if csv_reader.fieldnames != ['name', 'start', 'last_tracked', 'duration', 'closing_time']:
                # If the file has incorrect headers, reset the file
                open(filename, 'w').close()
            else:
                for row in csv_reader:
                    process_data[row['name']] = [row['start'], row['last_tracked'], row.get('duration', '0:00:00'), row.get('closing_time', '')]

    # Group & clean processes
    grouped_processes = defaultdict(list)
    for proc in process_list:
        try:
            proc_info = proc.info
            proc_name = proc_info['name'].lower()
            if proc_info['username'] and current_user in proc_info['username']:
                if proc_info['exe'] and 'C:\\Windows\\System32' not in proc_info['exe']:
                    if proc_name not in current_blacklist:
                        grouped_processes[proc_name].append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Process the grouped processes
    for proc_name, proc_infos in grouped_processes.items():
        active_processes.add(proc_name)
        if proc_name in process_data:
            start_time, last_tracked_time, prev_duration_str, closing_time = process_data[proc_name]
            previous_duration = timedelta(seconds=float(prev_duration_str))
        else:
            start_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            last_tracked_time = ''
            previous_duration = timedelta(0)
            closing_time = ''

        last_tracked_dt = datetime.strptime(last_tracked_time, "%Y-%m-%d %H:%M:%S") if last_tracked_time else current_time
        dif = (current_time - last_tracked_dt)
        print(f"{proc_name}: Difference {dif}")
        updated_duration = previous_duration + dif
        process_data[proc_name] = [start_time, current_time.strftime("%Y-%m-%d %H:%M:%S"), str(updated_duration.total_seconds()), closing_time]

    # Handle closed processes
    for name, times in process_data.items():
        if name.lower() not in active_processes and not times[3]:  # Process has closed and closing time is not set
            print(f"Closing process {name}")
            times[3] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            times[1] = None
            times[0] = None

    # Write updated data to file
    with open(filename, "w", newline='') as file:
        fieldnames = ['name', 'start', 'last_tracked', 'duration', 'closing_time']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for name, times in process_data.items():
            csv_writer.writerow({
                                 'name': name, 
                                 'start': times[0] if times[0] else '', 
                                 'last_tracked': times[1] if times[1] else '', 
                                 'duration': times[2], 
                                 'closing_time': times[3] if times[3] else ''
                               })

def parse_logs():
    log_data = defaultdict(list)
    for filename in glob.glob(os.path.join(att_data_folder, '*.csv')):
        with open(filename, 'r') as file:
            date = Path(filename).stem
            csv_reader = csv.DictReader(file)
            if csv_reader.fieldnames != ['name', 'start', 'last_tracked', 'duration', 'closing_time']:
                continue

            for row in csv_reader:
                app_name = row['name']
                duration = row['duration']
                log_data[(app_name, datetime.strptime(date, "%Y-%m-%d").date())].append((duration))
    return log_data

def calculate_statistics(log_data):
    daily_stats = defaultdict(timedelta)
    for (app_name, date), sessions in log_data.items():
        for duration in sessions:
            duration_td = timedelta(seconds=float(duration))
            daily_stats[(app_name, date)] += duration_td
    return daily_stats


def display_statistics():
    log_data = parse_logs()
    app_durations = calculate_statistics(log_data)

    stats_filename = os.path.join(att_data_folder, "app_usage_statistics.csv")
    with open(stats_filename, "w", newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['App Name', 'Total Duration'])
        
        print("App Usage Statistics:")
        for app_name, total_duration in app_durations.items():
            line = [f"App: {app_name}", f"Total Duration: {total_duration}"]
            csv_writer.writerow(line)
            print(', '.join(line))

    print(f"\nStatistics written to {stats_filename}")