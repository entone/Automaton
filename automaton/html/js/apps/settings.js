function DayNode(x, y, width, height, color, obj){
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.color = color;
    this.obj = obj;
}

DayNode.prototype.draw = function(canvas){
    var ctx = canvas.getContext("2d");
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.width, this.height);
}

DayNode.prototype.hit_test = function(x, y){
    if((x > this.x && x < (this.x+this.width)) && (y > this.y && y < (this.y+this.height))){
        return true;
    }
    return false;
}

Applications.Settings = function(){
    this.prefs = {};
    this.last = {};
    this.data = {};
    this.h_data = {};
}

Applications.Settings.prototype = new App();
Applications.Settings.constructor = Applications.Dashboard;

Applications.Settings.prototype.init = function(){    
    var range_template = $("#range_template").html();
    var trigger_template = $("#trigger_template").html();
    var pid_template = $("#pid_template").html();
    var repeater_template = $("#repeater_template").html();

    for(var i in loc.nodes){
        $("#content").append("<h2>Triggers</h2>");
        var output = "<ul class='thumbnails'>";
        for(var t in loc.nodes[i].triggers){
            console.log(loc.nodes[i].triggers[t]);
            output+= Mustache.to_html(trigger_template, loc.nodes[i].triggers[t]);            
        }
        $("#content").append(output+"</ul>");

        $("#content").append("<h2>Repeaters</h2>");
        var output = "<ul class='thumbnails'>";
        for(var r in loc.nodes[i].repeaters){
            output+=Mustache.to_html(repeater_template, loc.nodes[i].repeaters[r]);            
            draw_repeater(loc.nodes[i].repeaters[r].every, loc.nodes[i].repeaters[r].run_for, loc.nodes[i].repeaters[r].output);
        }
        $("#content").append(output+"</ul>");

        var ons = {};
        var ends = {};
        for(var c in loc.nodes[i].clocks){
            var clock = loc.nodes[i].clocks[c];
            var t = (clock.time.hour*60)+clock.time.minute;
            if(clock.state_change == true){
                ons[clock.output] = t;
            }else if(clock.state_change == false){
                ends[clock.output] = t;
            }
        }
        $("#content").append("<h2>Clocks</h2>");
        var output = "<ul class='thumbnails'>";
        for(t in ons){
            var obj = {start:ons[t], end:ends[t], output:t}
            output+= Mustache.to_html(range_template, obj);
        }
        $("#content").append(output+"</ul>");

        $("#content").append("<h2>PIDs</h2>");
        var output = "<ul class='thumbnails'>";
        for(var p in loc.nodes[i].pids){
            output+= Mustache.to_html(pid_template, loc.nodes[i].pids[p]);            
        }
        $("#content").append(output+"</ul>");
    }

    $(".run-for, .every").change(function(){
        var out = $(this).data('output');
        var every = parseInt($('#every'+out).val());
        var run_for = parseInt($('#run_for'+out).val());
        if(every && run_for){
            draw_repeater(every, run_for, out);
        }
    })

    $(".run-for").each(function(){
        var out = $(this).data('output');
        var every = parseInt($('#every'+out).val());
        var run_for = parseInt($('#run_for'+out).val());
        if(every && run_for){
            draw_repeater(every, run_for, out);
        }
    });

    $(".range").each(function(){
        var output = $(this).data('output');
        var start = $(this).data('start');
        var end = $(this).data('end');
        $(this).slider({
            range: true,
            min: 0,
            max: 1440,
            values: [start, end],
            animate:'fast',
            step:15,
            slide: function(event, ui) {
                $("#display"+output).html(format_time(ui.values[0])+" - "+format_time(ui.values[1]));
            }
        });
        $("#display"+output).html(format_time(start)+" - "+format_time(end));
    });
}

function draw_repeater(every, run_for, out){
    $("#repeater_display"+out).html("");
    var w = $("#repeater"+out).width()-30;
    var wid = parseInt(w)/1440;
    var rows=0;
    var daynode_height = 30;
    var cur_wid = 0;
    var colors = ['#FF0000'];
    var c = document.createElement("canvas");
    c.width = 800;
    c.height = 30;
    var cxt =  c.getContext("2d");
    cxt.clearRect(0, 0, w, 30);
    for(var i=0; i<1440; i+=every){
        var w = wid*run_for;
        var on = new DayNode(cur_wid, rows*daynode_height, w, daynode_height, colors[rows], {});
        on.draw(c);
        cur_wid+=w;
        var o_w = (every-run_for)*wid;
        var off = new DayNode(cur_wid, rows*daynode_height, o_w, daynode_height, "#dddddd");
        off.draw(c);
        cur_wid+=o_w;
    }
    $("#repeater_display"+out).append(c);
}

function format_time(minutes){
    var hours = String('00'+parseInt(minutes/60)).slice(-2);
    var min = String('00'+parseInt(minutes%60)).slice(-2);
    return hours+":"+min;
}

Applications.Settings.prototype.run = function(){}
Applications.Settings.prototype.stop = function(){}

window.application = Applications.Settings;