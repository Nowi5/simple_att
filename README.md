# Simple ATT - Application Time Tracker
The Simple Application Time Tracker (Simple ATT) is a sophisticated, lightweight tool designed to monitor and log application usage times on Windows (win32) operating systems.
It provides a straightforward solution for tracking the duration of application usage on a daily basis, making it especially valuable for overseeing the computer habits of children.

# Install & usage
1. Prerequisite: Ensure Python is installed on your Windows machine.
2. Run the Installer: Execute install.bat with administrator privileges.
The installation script automatically sets up a Windows service that checks for active applications every 5 minutes.
If an application is found running, the service increments its usage time and logs the data to a CSV file.
3. Viewing Statistics: To review application usage statistics, access the generated CSV files directly or execute the main file with the command stats to aggregate and display usage data.