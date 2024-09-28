# GroundSystem_GUI_Project

The GroundSytem_GUI_Project was created in response to a light request from the electrical team leader during ANCO-project 2022 to make a GUI to check telemetry.

This GUI system aims to be user-friendly and more convenient.

The map data of the area around the launch site in Ehime Prefecture can also be taken offline.

## Usage and Installation

1. Download the git repository

```shell
git clone git@github.com:Akatoki-Saidai/GroundSystem_GUI_Project.git
```

2. Install required modules

```shell
pip install -r requirements.txt
```

3. Run the web server

```shell
flask --app app run
```

or

```shell
python app.py
```

## Data Structure

The data is recognised by UART in comma-delimited format per line.

By default, the order is latitude, longitude, altitude, barometric pressure, RSSI, mode, battery, logging status, WiFi status and GNSS status.

```txt
0.0, 0.0, -17, 0.0, -50,Mode:wait, Bt:Middle, Log:OFF, WiFi:NG, GNSS:unlock
```

If binary data is to be sent or received, code must be added to convert it, or the converted data must be sent via UART.

## Contributor

ddd3h, takashin9
