<h1 align="center">wetter</h1>
<p align=center>
  <img src="https://raw.githubusercontent.com/ucyo/wetter-py/master/assets/undraw_weather.svg" width=500px/>
</p>
<p align=center>
<img alt="PyPI" src="https://img.shields.io/pypi/v/wetter?color=blue">
<img alt="PyPI - License" src="https://img.shields.io/pypi/l/wetter">
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/wetter">
<img alt="PyPI - Format" src="https://img.shields.io/pypi/format/wetter">
<img alt="PyPI - Status" src="https://img.shields.io/pypi/status/wetter">
<img alt="Docker Image Version (tag latest semver)" src="https://img.shields.io/docker/v/ucyo/wetter/latest?color=blue&label=docker">
</p>

This repository provides an Python application for checking the current
weather conditions at your favourite location. Additionally, it allows querying
historical data to run analysis on past measurements.

## Usage

The tool provides the `wetter` command line tool with several subcommands:

|command|Description|
|-------|-----------|
|`wetter latest`| Return latest measurement for your favourite city|
|`wetter update`|Update datastore with latest measurements|
|`wetter update --historical`|Update datastore with measurements from last year|
|`wetter compare --last-week`| Compare current weather w/ last week |
|`wetter compare --last-month`| Compare current weather w/ last month |
|`wetter compare --last-year`| Compare current weather w/ last year |
|`wetter compare --month`| Analyse specific month (average temperature & hottest days)|

Entering nothing but the `wetter` command will return the latest measurement
of the location similar to `wetter latest`.

## Getting started

There are several ways to install `wetter`. The easiest method would be to use pypi, download releases from GitHub or clone the repository and use e.g. [`poetry`](https://python-poetry.org/) to install it. If you don't want to install library immediately you could first try `wetter` by spinning up its docker image.

- Install using pypi

    ```bash
    pip install wetter  # the more courageous can add a --pre flag
    ```

- Install by (1) downloading the `.whl` from our releases and (2) install using `pip`

    ```bash
    python3 -m pip install wetter-0.3.0-py3-none-any.whl
    ```

- Install from source by cloning the repository and using `poetry`

    ```bash
    git clone https://github.com/ucyo/wetter-py.git  # clone the repo
    cd wetter-py/wetter  # change to library
    poetry install
    ```

- Get started using docker

    ```bash
    docker run -it ucyo/wetter:latest bash  # ucyo/wetter:testing for pre-releases
    ```

Checking if everything is working appropriately can be done using `wetter latest`. It should return something like the following:

```bash
> wetter latest
Currently it is 🌡️ 12.7°C and wind speed 🌬️ 13.0 km/h.
Latest measurement on 📅 2023-01-01 @ 01:00AM.
```

Now that we know everything is working as expected. Go ahead and update the database by executing `wetter update`.

> Your mileage might vary on getting the exact same output. The timestamp of the above command adjusts to the local time zone and might be different on yours.

## Configuration

I don't know why, but you might be interested in measurements from a different location. You can do this by adjusting the `wetter.toml` file. The location of the `wetter.toml` depends on your operating system. Additionally, you can find the locations of the measurement data itself i.e. `wetter.json` and logs i.e. `wetter.log`.

|Location|Operating System|
|--------|----------------|
|`/home/<username>/.config/wetter/`|Linux :penguin: (config)|
|`/home/<username>/.local/share/wetter/`|Linux :penguin: (data)|
|`/home/<username>/.local/state/wetter/log/wetter.log`|Linux :penguin: (log)|
|`/Users/<username>/Library/Application Support/wetter/`|macOS :apple: (config & data)|
|`/Users/<username>/Library/Logs/wetter/`|macOS :apple: (logs)|
|`C:\Users\<username>\AppData\Local\ucyo\wetter`|Windows :window: (config & data)|
|`C:\Users\<username>\AppData\Local\ucyo\wetter\logs`|Windows :window: (logs)|

If you have problems finding the proper location there is a gimmick that got you covered.
The path to the configuration file is returned by `wetter configure --config`.
The logging level can be set by the `WETTER_LOG` environmental variable.

### Sample configuration

```toml
[location]
lat = 49
lon = 8.41
```

The configuration file is very basic. Simply type in the lat/lon position :earth_africa: of
your favourite location.
You might use an online service to look up the coordinates of a certain city like a [LatLongFinder](https://www.latlong.net/).

### Sample database

```json
{
    "lat": 49,
    "lon": 8.41,
    "version": 1,
    "data": {
        "index": ["temperature", "wind"],
        "columns": ["2023-01-01T00:00:00.000000+0000", "2023-01-01T01:00:00.000000+0000"],
        "data": [[7.7, 12.7], [6.8, 13.0]],
    },
}
```

The json database stores only the data for a single position. Those are included
in the database with the `lat` and `lon` tags.
This information aligned on system start with the configuration file.
Should they not match within 1 degree (in the above case for latitude `48 <= lat <= 50`),
then a reset will be triggered.

> Note: The update to the new location happens without user interaction.
> The tool assumes the user changed the settings knowingly and will update the
> the database on the next execution.

## Setup background daemon

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

Go back :point_up: Just use `cron`. All that glistens is not gold :eyes:

#### tl;dr

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

#### Detailed

First you need to create the necessary files for a systemd service.
This involves two files:
First, the service file which defines the background process in `wetter.service`.
Afterwards, the scheduler file which defines when the background process needs to be run i.e. `wetter.timer`.

```bash
wetter configure --systemd > wetter.service  # generate service file
wetter configure --systemdtimer > wetter.timer # generate schedule file
```

> Note: Timers are not mandatory to run services on a certain schedule. One could use the the `systemd-run` command to schedule calls to services without a timer configuration. See [systemd-run manpage](https://man.archlinux.org/man/systemd-run.1) on ArchLinux for details.

Now that have the necessary files set up, need to make them available
for systemd. The most common location of systemd files is `/etc/systemd/system/`.
Therefore you need to move the files to that location.

```bash
mv wetter.service /etc/systemd/system/wetter.service  # move service file
mv wetter.timer /etc/systemd/system/wetter.timer  # schedule service
```

> Note: Fedora/RedHat/CentOS users might need to adjust the above mentioned location.

Before you can enable and start the service you must address a caveat of systemd.
The systemd daemon is not allowed to access binaries in home directories of users.
That's why you need to create a symbolic link in `/usr/bin` to allow
the service to execute updates on the database. That can be done using
the following command:

```bash
ln -s $(which wetter) /usr/bin/wetter
```

This concludes the setup process. Now the service can be enabled and started
using the `systemctl` command.

- Enabling the systemd service `systemctl enable wetter.service`
- Starting the systemd service `systemctl start wetter.service`

## Resources

The measurement data is being gathered using the archive and forecast API
from [Open-Meteo.com](https://open-meteo.com/) :heart:
