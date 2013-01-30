var off = (new Date().getTimezoneOffset());

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
Applications.Settings.constructor = Applications.Settings;

Applications.Settings.prototype.init = function(){    
    var range_template = $("#range_template").html();
    var ph_template = $("#range_template").html();
    var temperature_template = $("#range_template").html();
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
            console.log(loc.nodes[i].clocks[c]);
            var clock = loc.nodes[i].clocks[c];
            var t = (clock.time.hour*60)+clock.time.minute;
            var ob = {time:t, display:clock.output};
            if(clock.state_change == true){
                ons[clock.id] = ob;
            }else if(clock.state_change == false){
                ends[clock.id] = ob;
            }
        }
        $("#content").append("<h2>Clocks</h2>");
        var output = "<ul class='thumbnails'>";
        for(t in ons){
            var obj = {start:ons[t].time, end:ends[t].time, id:t, output:ons[t].display}
            output+= Mustache.to_html(range_template, obj);
        }
        $("#content").append(output+"</ul>");

        $("#content").append("<h2>PIDs</h2>");
        var output = "<ul class='thumbnails'>";
        for(var p in loc.nodes[i].pids){
            console.log(loc.nodes[i].pids);
            output+= Mustache.to_html(pid_template, loc.nodes[i].pids[p]);
        }
        $("#content").append(output+"</ul>");
    }

    $(".run-for, .every").change(function(){
        var out = $(this).data('output');
        console.log(out);
        var every = parseInt($('#every'+out).val());
        var run_for = parseInt($('#run_for'+out).val());
        if(every && run_for){
            draw_repeater(every, run_for, out);
        }
    })

    $(".run-for").each(function(){
        var out = $(this).data('output');
        console.log(out);
        var every = parseInt($('#every__'+out).val());
        var run_for = parseInt($('#run_for__'+out).val());
        if(every && run_for){
            draw_repeater(every, run_for, out);
        }
    });

    $(".range").each(function(){
        var output = $(this).data('output');
        var start = $(this).data('start');
        var end = $(this).data('end');
        if(start > end){
            end = (1440+end)-off;
        }else{
            end = end-off;
        }
        start-=off;
        $(this).slider({
            range: true,
            min: 0,
            max: 1440,
            values: [start, end],
            animate:'fast',
            step:15,
            slide: function(event, ui){
                $("#display"+output).html(format_time(ui.values[0])+" - "+format_time(ui.values[1]));
            }
        });
        $("#display"+output).html(format_time(start)+" - "+format_time(end));
    });    
    $("#content").prepend("<button class='save btn btn-primary pull-right'>Save</button>");
    $("#content").append("<button class='last save btn btn-primary pull-right'>Save</button>");
    var that = this;
    $(".save").click(function(){
        that.save();
    });

}

Applications.Settings.prototype.save = function(){
    var obj = {node:$("#node").val()};
    $(".setting").each(function(){
        var id = $(this).data('id');
        obj[id] = {};
        $(this).children("input").each(function(){
            obj[id][$(this).attr('id')] = $(this).val();
        })
    });    
    $(".range").each(function(){
        var id = $(this).parent().data('id');
        obj[id] = $(this).slider('option', 'values');
        var min = obj[id][0]+off > 1440 ?  obj[id][0]+off - 1440 : obj[id][0]+off
        var max = obj[id][1]+off > 1440 ?  obj[id][1]+off - 1440 : obj[id][1]+off
        obj[id][0] = min
        obj[id][1] = max;
    })
    console.log(obj);
    this.post("/settings/save/", JSON.stringify(obj), function(res){
        console.log(res);
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
    c.width = w;
    c.height = 20;
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

Applications.Settings.prototype.run = function(){}
Applications.Settings.prototype.stop = function(){}

window.application = Applications.Settings;