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
    $("#start").slider({
        range: true,
        min: 0,
        max: 1440,
        values: [ 75, 300 ],
        animate:'fast',
        step:15,
        slide: function(event, ui) {
            $("#display").html(format_time(ui.values[0])+" - "+format_time(ui.values[1]));
        }
    });

    $("#run_for, #every").change(function(){
        var every = parseInt($('#every').val());
        var run_for = parseInt($('#run_for').val());
        if(every && run_for){
            draw_repeater(every, run_for);
        }        
    })
}

function draw_repeater(every, run_for){
    $("#repeater_display").html("");
    var wid = parseInt(800)/1440;
    var rows=0;
    var daynode_height = 30;
    var cur_wid = 0;
    var colors = ['#FF0000'];
    var c = document.createElement("canvas");
    c.width = 800;
    c.height = 30;
    var cxt =  c.getContext("2d");
    cxt.clearRect(0, 0, 800, 40);
    for(var i=0; i<1440; i+=every){
        console.log(i);
        var w = wid*run_for;
        var on = new DayNode(cur_wid, rows*daynode_height, w, daynode_height, colors[rows], {});
        on.draw(c);
        cur_wid+=w;
        var o_w = (every-run_for)*wid;
        var off = new DayNode(cur_wid, rows*daynode_height, o_w, daynode_height, "#dddddd");
        off.draw(c);
        cur_wid+=o_w;
    }
    $("#repeater_display").append(c);
}

function format_time(minutes){
    var hours = String('00'+parseInt(minutes/60)).slice(-2);
    var min = String('00'+parseInt(minutes%60)).slice(-2);
    return hours+":"+min;
}

Applications.Settings.prototype.run = function(){}
Applications.Settings.prototype.stop = function(){}

window.application = Applications.Settings;