# SpeedTestLogger
Sick of your internet provider gas lighting you? This is a python script you can schedule to track your internet speed into a shareable gsheet. Stick it to the man :P


## Steps to use:

#### 1.) Use [this great tutorial](https://www.makeuseof.com/tag/read-write-google-sheets-python/) to set up your gsheet!

    The program is expecting your sheet to be set up with the following header/column layout:
    --------------------------------------------------------------------------------------------------------------------
    | Date | Time | Server Name | Download (Mbps) | Upload (Mbps) | Ping (ms) |     |     |     |     |     | Last Row |
    --------------------------------------------------------------------------------------------------------------------

#### 2.) Place your gsheet service key in the same directory as the script and name it `gsheet-creds.json` (or just pass the file name as a cmd line argument).

#### 3.) Update the `logger.config` file to reflect your preferences.

#### 4.) Then use [Windows Scheduler](https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10) to schedule the script to run, or [cron](https://www.hostinger.com/tutorials/cron-job) (if your unix).
