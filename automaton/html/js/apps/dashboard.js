var bar_options = {
    series:{
        bars:{
            show:true,
            barWidth:(17 * 60 * 60 * 1000),
            align: "center",
        },
    },
    xaxis: {
        mode: "time",
        timeformat:"%m/%d",
        minTickSize: [1, "day"],
    },
    grid:{
        color: "#000000",
        backgroundColor: "#eeeeee",
        borderWidth: 3,
        borderColor: "#dddddd",
        hoverable: true,
    },
    legend:{
        backgroundColor:"#FFFFFF",
        position: "nw",
    },
};

Applications.Dashboard = function(){
    this.prefs = {};
    this.last = {};
    this.data = {};
    this.h_data = {};
}

Applications.Dashboard.prototype = new App();
Applications.Dashboard.constructor = Applications.Dashboard;

Applications.Dashboard.prototype.init = function(){
    for(var n in loc.nodes){
        var tot = 0;
        for(var i in loc.nodes[n].sensors){
            var s = loc.nodes[n].sensors[i];
            s.color = colors[tot];
            var sensor = sensors[s.type];
            if(sensor){
                s.decorator = sensor.decorator;
                this.prefs[s.id] = {color:colors[tot], decorator:decorators[s.type]}
                this.last[s.id] = s.value;
                this.data[s.id] = [];
                this.h_data[s.id] = {data:[], color:colors[tot]};
                tot++;
            }
        }
    }
    var template = document.getElementById('dashboard_template').innerHTML;
    var output = Mustache.to_html(template, {nodes:loc.nodes});
    document.getElementById('content').innerHTML+= output;
    console.log(averages['ph']);
    $.plot($("#avg_watertemp"), [{label:"Daily Average Water Temperature", data:averages['water-temperature'], color: colors[0]}], bar_options);
    $.plot($("#avg_ph"), [{label:"Daily Average PH", data:averages['ph'], color: colors[1]}], bar_options);
    $.plot($("#avg_temp"), [{label:"Daily Average Temperature", data:averages['temperature'], color: colors[2]}], bar_options);
    $.plot($("#avg_humidity"), [{label:"Daily Average Humidity", data:averages['humidity'], color: colors[3]}], bar_options);
    $.plot($("#avg_waterlevel"), [{label:"Daily Average Water Level", data:averages['water-level'], color: colors[4]}], bar_options);
    $.plot($("#avg_do"), [{label:"Daily Average DO", data:averages['do'], color: colors[5]}], bar_options);
    $.plot($("#avg_do-percentage"), [{label:"Daily Average DO Percentage", data:averages['do-percentage'], color: colors[6]}], bar_options);
    $.plot($("#avg_orp"), [{label:"Daily Average ORP", data:averages['orp'], color: colors[7]}], bar_options);
    $(".graph").bind("plothover", function (event, pos, item) {
        if (item) {
            if (previousPoint != item.dataIndex) {
                previousPoint = item.dataIndex;

                $("#tooltip").remove();
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                showTooltip(item.pageX, item.pageY, y);
            }
        }
        else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
}

Applications.Dashboard.prototype.run = function(){}
Applications.Dashboard.prototype.stop = function(){}

window.application = Applications.Dashboard;
