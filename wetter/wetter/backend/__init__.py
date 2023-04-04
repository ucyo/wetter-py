"""Backend of the wetter library.

This module handles the measurement data.
It is reponsible for defining a unified interface to the local data.
The includes the json structure of the data to be saved on the local machine.
as well as the update of the data using open API services.
The module defines three components:

- `WetterDB`: Read/Write/Update of the database
- `APIForWeatherData`: Definition of an API for access different WetterAPI services
- `QueryTicket`: Common data structure to abstract and regulate query parameters

The `WetterDB` reads and write data to the json backend store.
This can handle all the day to day queries of the cli tool.
If an update is necessary, then the other two components come in play.

The update process itself is a two step process.
First, a `QueryTicket` is defined.
It defines the data to be gathered from outside services e.g. [OpenMeteo](https://open-meteo.com/).
Afterwards this ticket is given to an API service for weather data.
Currently there is the OpenMeteo WeatherAPI service implemented.
Additional service might be added later on.
All API services need to be subclasses of `APIForWeatherData`.
This allows for an easy interchange of APIs.
"""
