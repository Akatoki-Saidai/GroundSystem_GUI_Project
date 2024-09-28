import json
from math import floor
import random
import time
from datetime import datetime
from flask import (
    Flask,
    Response,
    render_template,
    stream_with_context,
    request,
    redirect,
    url_for,
    send_file,
)
import glob
import serial
import os
import urllib.request, urllib.error
import time
import requests
import json
import csv
import copy
import serial.tools.list_ports

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(["csv"])
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def internet_on():
    try:
        urllib.request.urlopen(url="http://www.google.co.jp/", timeout=1)
        return True
    except urllib.error.URLError as err:
        return False


selected_port = "未接続"


@app.route("/")
def index():
    setting_data = json.load(open(".config", "r"))
    port_ls = serial.tools.list_ports.comports()
    port_ls = [i.device for i in port_ls]
    if setting_data["selected_port"] in port_ls:
        return render_template(
            "index.html", selected_port=setting_data["selected_port"]
        )
    else:
        return render_template("index.html", selected_port="未接続")


@app.route("/settings", methods=["GET", "POST"])
def setting():
    setting_data = json.load(open(".config", "r"))
    port_ls = serial.tools.list_ports.comports()
    port_ls = [i.device for i in port_ls]
    if request.method == "GET":
        if setting_data["selected_port"] in port_ls:
            selected_port = f'<option selected value="{setting_data["selected_port"]}">{setting_data["selected_port"]}</option>'
            port_ls.remove(setting_data["selected_port"])
        else:
            selected_port = f'<option selected value="">未接続</option>'

        gpslat = setting_data["gpslat"]
        gpslon = setting_data["gpslon"]

        default_output_file = setting_data["default_output_file"]
        return render_template(
            "settings.html",
            port_ls=port_ls,
            selected_port=selected_port,
            gpslat=gpslat,
            gpslon=gpslon,
            default_output_file=default_output_file,
            alert="",
        )

    else:
        with open(".config", "w") as f:
            json.dump(request.form, f, indent=4)
        if request.form["selected_port"] == "":
            selected_port = f'<option selected value="">未接続</option>'
        else:
            selected_port = request.form["selected_port"]

        return render_template(
            "settings.html",
            port_ls=port_ls,
            selected_port=selected_port,
            gpslat=request.form["gpslat"],
            gpslon=request.form["gpslon"],
            default_output_file=request.form["default_output_file"],
            alert='<div class="alert alert-success" role="alert"><b>保存しました</b></div>',
        )


@app.route("/data")
def data():
    setting_data = json.load(open(".config", "r"))
    selected_port = setting_data["selected_port"]

    def generate_data():
        if not selected_port == "":
            ser = serial.Serial(selected_port, 9600, timeout=None)

            if os.path.isfile(f'downlinkdata/{setting_data["default_output_file"]}'):
                file = open(f'downlinkdata/{setting_data["default_output_file"]}', "a")
                writer = csv.writer(file)
            else:
                file = open(f'downlinkdata/{setting_data["default_output_file"]}', "w")
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "lat",
                        "lng",
                        "alt",
                        "pres",
                        "rssi",
                        "mode",
                        "bt",
                        "log",
                        "wifi",
                        "gnss",
                        "timestamp",
                        "",
                        "",
                        "",
                        "",
                    ]
                )

            time_sta = 0
            alt_sta = 0
            while True:
                DATA = []
                linep = ser.readline().decode("utf-8")
                # linep = "0.0, 0.0, -17, 0.0, -50,Mode:wait, Bt:Middle, Log:OFF, WiFi:NG, GNSS:unlock"
                # time.sleep(1)

                time_end = time.perf_counter()
                tim = time_end - time_sta

                line = linep.replace("\r\n", "")
                DATA = line.split(",")
                print(DATA)
                dnow = datetime.now()
                DATA.append(dnow.strftime("%Y/%m/%d %H:%M:%S"))

                Mode = copy.copy(DATA[5])
                Battery = copy.copy(DATA[6])
                Log = copy.copy(DATA[7])
                Wifi = copy.copy(DATA[8])
                GNSS = copy.copy(DATA[9])

                Mode = Mode.replace("Mode:", "")
                Battery = Battery.replace("Bt:", "")
                Log = Log.replace("Log:", "")
                Wifi = Wifi.replace("WiFi:", "")
                GNSS = GNSS.replace("GNSS:", "")

                DATA[5] = Mode
                DATA[6] = Battery
                DATA[7] = Log
                DATA[8] = Wifi
                DATA[9] = GNSS

                writer.writerow(DATA)
                file.flush()
                lat = float(DATA[0])
                lng = float(DATA[1])

                altitude = int(DATA[2])
                dif_alt = altitude - alt_sta
                pressure = float(DATA[3])
                RSSI = int(DATA[4])

                D_lat = floor(lat)
                M_lat = floor((lat - D_lat) * 60)
                S_lat = round(((lat - D_lat) * 60 - M_lat) * 60 * 1e5) / 1e5
                D_lng = floor(lng)
                M_lng = floor((lng - D_lng) * 60)
                S_lng = round(((lng - D_lng) * 60 - M_lng) * 60 * 1e5) / 1e5

                if time_sta == 0:
                    velocity = 0
                else:
                    velocity = round(dif_alt / tim, 1)
                time_sta = time_end
                alt_sta = altitude

                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%M:%S"),
                        "altitude": altitude,
                        "pressure": pressure,
                        "RSSI": RSSI,
                        "latitude": lat,
                        "longitude": lng,
                        "D_lat": D_lat,
                        "M_lat": M_lat,
                        "S_lat": S_lat,
                        "D_lng": D_lng,
                        "M_lng": M_lng,
                        "S_lng": S_lng,
                        "Mode": Mode,
                        "Battery": Battery,
                        "Log": Log,
                        "Wifi": Wifi,
                        "GNSS": GNSS,
                        "velocity": velocity,
                        "console": linep,
                        "gpslat": float(setting_data["gpslat"]),
                        "gpslon": float(setting_data["gpslon"]),
                    }
                )
                yield f"data:{json_data}\n\n"

    response = Response(
        stream_with_context(generate_data()), mimetype="text/event-stream"
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route("/offlinemap/<x>/<y>/<z>")
def offlinemap(x, y, z):
    filename = f"mapdata/ggSatelliteTiles/{z}/{x}/{y}.png"
    if os.path.isfile(filename):
        return send_file(filename)
    elif internet_on():
        return redirect(f"https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}")
    else:
        return send_file("mapdata/black.png")


@app.route("/sim")
def sim():
    return send_file("")


@app.route("/download", methods=["GET", "POST"])
def download_data():
    setting_data = json.load(open(".config", "r"))
    selected_port = setting_data["selected_port"]
    if request.method == "POST":
        filename = request.form["default_output_file"]
        return send_file(
            f'downlinkdata/{setting_data["default_output_file"]}',
            as_attachment=True,
            download_name=filename,
            mimetype="text/csv",
        )


if __name__ == "__main__":
    app.run(debug=False, threaded=True)