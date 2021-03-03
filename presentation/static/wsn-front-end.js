var dataPointsHumidity = [];
var chartHumidity;
var dataPointsTemp = [];
var chartTemp;
var dataPointsWind = [];
var chartWind;
var dataPointsFlame = [];
var chartFlame;
var stations = [];
var index = 0;
var dataPointsHumidityMean = [];
var dataPointsTempMean = [];
var dataPointsWindMean = [];
var INIT_VALUES = 5;
var INIT_STATS = 5;

$(document).ready(function(){
    $(".sidenav").sidenav();

    $.getJSON("http://localhost:8080/wsn", function(datarcv){
    var data = JSON.parse(datarcv);
        var html_code = "";
        for(var i = 0; i < data.agents_jid.length; i++){
            stations[i] = data["agents_jid"][i];
            html_code += '<li><a href="#" onclick="viewStation('+i+')">'+data["agents_jid"][i]+'</a></li>';
        }
        $("#mobile-demo").html(html_code);
        $("#state").text("Working");
        viewStation(0);
        schedule();
        window.setInterval(schedule, 10000);
    });
});

function schedule(){
    renderInitAgentsValues(stations[index], 1);
    renderInitAgentsStats(stations[index], 1);
    getAgentState(stations[index]);
}

function viewStation(agent_jid_index){
    index = agent_jid_index;
    dataPointsHumidity = [];
    dataPointsTemp = [];
    dataPointsWind = [];
    dataPointsFlame = [];
    dataPointsHumidityMean = [];
    dataPointsTempMean = [];
    dataPointsWindMean = [];


    chartHumidity = new CanvasJS.Chart("chartContainerHum", {
        theme: "light2",
        title: {
            text: "Humidity"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: "Humidity"
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsHumidity
            }, {
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            name: "Average",
            type: "spline",
            dataPoints: dataPointsHumidityMean
            }]
    });

    chartTemp = new CanvasJS.Chart("chartContainerTemp", {
        theme: "light2",
        title: {
            text: "Temperature"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: "C°"
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsTemp
            }, {
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            name: "Average",
            type: "spline",
            dataPoints: dataPointsTempMean
            }]
    });

    chartWind = new CanvasJS.Chart("chartContainerWind", {
        theme: "light2",
        title: {
            text: "Wind"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: "Km/h"
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsWind
            }, {
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            name: "Average",
            type: "spline",
            dataPoints: dataPointsWindMean
            }]
    });

    chartFlame = new CanvasJS.Chart("chartContainerFlame", {
        theme: "light2",
        title: {
           text: "Flame"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: ""
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsFlame
        }]
    });

    render();
    $("#station").text(stations[index]);
    getAgentState(stations[index])
    renderInitAgentsValues(stations[index], INIT_VALUES);
    renderInitAgentsStats(stations[index], INIT_STATS);
    $(".sidenav").sidenav('close');
}

function getAgentJIDs(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.status == 200){
            var data = JSON.parse(this.responseText);
            var html_code = "";
            for(var i = 0; i < data.agents_jid.length; i++){
                stations[i] = data["agents_jid"][i];
                html_code += '<li class="tab"><div> '+data["agents_jid"][i]+' </div></li>';
            }
            $("#agent_jid").html(html_code);
        }
    };
    xmlhttp.open("GET", "http://localhost:8080/wsn", true);
    xmlhttp.send();
}

function getAgentState(agent_jid){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            $("#state").text(data["state"]);
        }
    };
    xmlhttp.open("GET", "http://localhost:8080/state/"+agent_jid, true);
    xmlhttp.send();
}

function renderInitAgentsValues(jid, limit){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            console.log(data);
            for(var i = (data.length - 1); i >= 0 ; i--){
                dataPointsHumidity.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["hum"])});
                dataPointsTemp.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["temp"])});
                dataPointsWind.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["wind"])});
                if(data[i]["flame"] == true){
                        dataPointsFlame.push({x: Date.parse(data[i]["timestamp"]), y: 1});
                } else {
                      dataPointsFlame.push({x: Date.parse(data[i]["timestamp"]), y: 0});
                }
            }
            render();
        }
    };
    xmlhttp.open("GET", "http://localhost:8080/value/"+jid+"?limit="+limit, true);
    xmlhttp.send();
}

function renderInitAgentsStats(jid, limit){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            console.log(data);
            for(var i = (data.length - 1); i >= 0 ; i--){
                dataPointsHumidityMean.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["hum_avg"])});
                dataPointsTempMean.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["temp_avg"])});
                dataPointsWindMean.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["wind_avg"])});
            }
            $("#hum_max").text("Max: "+data[0]["hum_max"]+" %");
            $("#hum_min").text("Min: "+data[0]["hum_min"]+" %");
            $("#temp_max").text("Max: "+data[0]["temp_max"]+" C°");
            $("#temp_min").text("Min: "+data[0]["temp_min"]+" C°");
            $("#wind_max").text("Max: "+data[0]["wind_max"]+" Km/h");
            $("#wind_min").text("Min: "+data[0]["wind_min"]+" Km/h");
            render();
        }
    };
    xmlhttp.open("GET", "http://localhost:8080/statistics/"+jid+"?limit="+limit, true);
    xmlhttp.send();
}

function render(){
      chartHumidity.render();
      chartTemp.render();
      chartWind.render();
      chartFlame.render();
}
