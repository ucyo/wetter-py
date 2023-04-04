# Template for Python

## Setup background process

There are several ways to enable a background process on Unix systems (incl. macOS).
The easiest and most supported is to setup using `cron`.
Another scheduling daemon is `systemd`.
In the following are the instructions for both systems.

> Spoiler alert! Use `cron`.

### Crontab

Execute the following command:

```bash
(crontab -l ; echo "5 * * * * wetter update") 2> /dev/null | sort -u | crontab -
```

Check [crontab guru](https://crontab.guru/) for details on the scheduling syntax.

### Systemd

### tl;dr

In user space:

```bash
wetter configure --systemd > wetter.service  # generate service file
wetter configure --systemdtimer > wetter.timer # generate schedule file
```

As privileged user:

```bash
ln -s $(which wetter) /usr/bin/wetter  # get binary out of home
mv wetter.service /etc/systemd/system/wetter.service  # move service file
mv wetter.timer /etc/systemd/system/wetter.timer  # move schedule service
systemctl enable wetter.service  # enable service
systemctl start wetter.service  # start service
```

### Detailed

First we need to create the necessary files for a systemd service.
This involves two files:
First, the service file which defines the background process in `wetter.service`.
Afterwards, the scheduler file which defines when the background process needs to be run i.e. `wetter.timer`.

```bash
wetter configure --systemd > wetter.service  # generate service file
wetter configure --systemdtimer > wetter.timer # generate schedule file
```

> Note: Timers are not mandatory to run services on a certain schedule. One could use the the `systemd-run` command to schedule calls to services without a timer configuration. See [systemd-run manpage](https://man.archlinux.org/man/systemd-run.1) on ArchLinux for details.

Now that we have the necessary files set up, we need to make them available
for systemd. The most common location of systemd files is `/etc/systemd/system/`.
Therefore we need the just created files to this location.

```bash
mv wetter.service /etc/systemd/system/wetter.service  # move service file
mv wetter.timer /etc/systemd/system/wetter.timer  # schedule service
```

> Note: Fedora/RedHat/CentOS users might need to adjust the above mentioned location.

Before we can enable and start the service, we must address a caveat of systemd.
The systemd daemon is not allowed to access binaries in home directories of users.
That's why we need to create a symbolic link in `/usr/bin` to allow
the service to execute updates on the database. That can be done using
the following command:

```bash
ln -s $(which wetter) /usr/bin/wetter
```

This concludes the setup process. Now the service can be enabled and started
using the `systemctl` command.

- Enabling the systemd service `systemctl enable wetter.service`
- Starting the systemd service `systemctl start wetter.service`
