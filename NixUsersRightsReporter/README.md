## Users Rights Reports
If you have a list of servers and you want to see a users rights reports, you can use _Reports.generateUsersRightReport_. This script supports Linux (RHEL (4,5,6,7), didn't test on Ubuntu/Debian yet), Solaris (8,9,10) and AIX (4,5,6,7). The syntax is as below:

```
Usage: generateUsersRightsReport.py [options] -f servers_list_file

Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  servers list file, in format of Application,ServerName
                        (mandatory)
  -o FILE, --output-directory=FILE
                        output directory where output files will be generated.
                        There will be one file per application
  -v                    If -v is set, the output is also displayed on the
                        screen. Without using -v, you will only get the output
                        files
```
The script accepts an input file, in format of ApplicationName,ServerName and then goes through the file and for every server, provides the list of users, showing which groups a user belongs to, if the user is currently locked and also provides the sudo permissions of that user. Then it'll produce a separate output file (either in the current directory you are running the script or in directory specified in -o) for every application name, containing its servers with their user report.

Because I had to cover some really old boxes that didn't support 'sudo -U username -l', I had to use an external python script that actually parsed the sudoers file.

A sample run would be:

```
python -m Reports.generateUsersRightsReport -f ~/tmp/server.list -o ~/tmp -v
```
The content of ~/tmp/server.list:
```
amazon,aws-devbox1
amazon,aws-devbox2
amazon,aws-devbox3
```

Please notice that the script attempts to SSH to the box as root, assuming that it can connect without password (your key is in the box's root .ssh/authorized_key file).
