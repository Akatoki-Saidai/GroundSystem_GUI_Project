$(document).ready(function () {
    const altitude_config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "value",
                backgroundColor: 'rgb(255, 0, 0)',
                borderColor: 'rgb(255, 0, 0)',
                data: [],
                fill: false,
            }
        ],
        },
        options: {
            legend: {
                display: false
            },  
            responsive: true,
            title: {
                display: true,
                text: 'altitude'
            },
            /*tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
            },*/
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '[m]'
                    }
                }]
            }
        }
    };
    const pressure_config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "value",
                backgroundColor: 'rgb(0, 255, 0)',
                borderColor: 'rgb(0, 255, 0)',
                data: [],
                fill: false,
            }
        ],
        },
        options: {
            legend: {
                display: false
            },
            responsive: true,
            title: {
                display: true,
                text: 'pressure'
            },
            /*tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
            },*/
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '[hPa]'
                    }
                }]
            }
        }
    };
    const RSSI_config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "value",
                backgroundColor: 'rgb(0, 0, 255)',
                borderColor: 'rgb(0, 0, 255)',
                data: [],
                fill: false,
            }
        ],
        },
        options: {
            legend: {
                display: false
            },
            responsive: true,
            title: {
                display: true,
                text: 'RSSI'
            },
            /*tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
            },*/
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '[dBm]'
                    },
                    ticks: {        
                        suggestedMin: -140,
                        suggestedMax: 0,
                        stepSize: 20
                    }
                }]
            }
        }
    };
    let $Degree = document.getElementById("Degree");
    let $DMS = document.getElementById("DMS");
    
    let $D_table = document.getElementById("D_table");
    let $DMS_table = document.getElementById("DMS_table");

    reset_styles = function() {
        $Degree.classList.remove("active");
        $DMS.classList.remove("active");
        $D_table.classList.remove("active");
        $DMS_table.classList.remove("active");
    };
    $Degree.addEventListener("click", function() {
        reset_styles();
        if (this.classList.toggle("active")) {
            $D_table.classList.toggle("active");
        }
    })
    $DMS.addEventListener("click", function() {
        reset_styles();
        if (this.classList.toggle("active")) {
            $DMS_table.classList.toggle("active");
        }
    });


    $Degree.classList.toggle("active")
    $D_table.classList.toggle("active")
    var map = L.map('map').setView([33.021750, 133.016611], 10);
    
    L.tileLayer('http://127.0.0.1:5000/offlinemap/{x}/{y}/{z}', {
        maxZoom: 19,
        attribution: 'OFFLINE MAP',
    }).addTo(map);
    //var marker = L.marker([40, 140]).addTo(map);

    const marker_queue = [];
    const marker_queue2 = [];
    const prediction = [];

    const altitude_context = document.getElementById('altitude_canvas').getContext('2d');
    const pressure_context = document.getElementById('pressure_canvas').getContext('2d');
    const RSSI_context = document.getElementById('RSSI_canvas').getContext('2d');

    const altitude_lineChart = new Chart(altitude_context, altitude_config);
    const pressure_lineChart = new Chart(pressure_context, pressure_config);
    const RSSI_lineChart = new Chart(RSSI_context, RSSI_config);

    const source = new EventSource("/data");

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        //marker.setLatLng([data.latitude, data.longitude]);
        //var marker = L.marker([data.latitude, data.longitude]).addTo(map);
        var lat60 = data.D_lat + "°" + data.M_lat + "'" + data.S_lat;
        var lng60 = data.D_lng + "°" + data.M_lng + "'" + data.S_lng;
        
        var marker = L.marker([data.latitude, data.longitude]).bindPopup(data.latitude + "<br>" + data.longitude + "<br></br>" + lat60 + "<br>" + lng60).addTo(map).on('mouseover', function() {marker.openPopup();});

        var marker2 = L.marker([data.gpslat, data.gpslon]).bindPopup("ME").addTo(map);

        if(marker_queue.length === 20){
            map.removeLayer(marker_queue[0]);
            marker_queue.shift();
        }
        marker_queue.push(marker);

        if(marker_queue2.length === 1){
            map.removeLayer(marker_queue2[0]);
            marker_queue2.shift();
        }
        marker_queue2.push(marker2);

        document.getElementById('latitude').innerHTML = data.latitude;
        document.getElementById('longitude').innerHTML = data.longitude;
        document.getElementById('latitude60').innerHTML = lat60;
        document.getElementById('longitude60').innerHTML = lng60;

        

        if (altitude_config.data.labels.length === 20) {
            altitude_config.data.labels.shift();
            altitude_config.data.datasets[0].data.shift();
        }
        altitude_config.data.labels.push(data.time);
        altitude_config.data.datasets[0].data.push(data.altitude);
        altitude_lineChart.update();


        if (pressure_config.data.labels.length === 20) {
            pressure_config.data.labels.shift();
            pressure_config.data.datasets[0].data.shift();
        }
        pressure_config.data.labels.push(data.time);
        pressure_config.data.datasets[0].data.push(data.pressure);
        pressure_lineChart.update();


        if (RSSI_config.data.labels.length === 20) {
            RSSI_config.data.labels.shift();
            RSSI_config.data.datasets[0].data.shift();
        }
        RSSI_config.data.labels.push(data.time);
        RSSI_config.data.datasets[0].data.push(data.RSSI);
        RSSI_lineChart.update();

        document.getElementById('Mode').innerHTML = data.Mode
        document.getElementById('Battery').innerHTML = data.Battery
        document.getElementById('Log').innerHTML = data.Log
        document.getElementById('Wifi').innerHTML = data.Wifi
        document.getElementById('GNSS').innerHTML = data.GNSS
        document.getElementById('altitude').innerHTML = Math.round(data.altitude * 100)/100;
        document.getElementById('pressure').innerHTML = Math.round(data.pressure * 100)/100;
        document.getElementById('RSSI').innerHTML = Math.round(data.RSSI * 100)/100;
        document.getElementById('velocity').innerHTML = data.velocity;
        document.getElementById('console').innerHTML = data.console;
    };
})

