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

function Node(obj){
    for(var key in obj){
        this[key] = obj[key];
    }
    this.prefs = {}
    this.data = {};
    this.last = {};
    this.h_data = {};
    var node_template = document.getElementById('node_template').innerHTML;
    var tot = 0;
    for(var i in this.sensors){
        var s = this.sensors[i];
        s.color = colors[tot];
        this.prefs[s.id] = {color:colors[tot], decorator:decorators[s.type]}
        this.last[s.id] = s.value;
        this.data[s.id] = [];
        this.h_data[s.id] = {data:[], color:colors[tot]};
        tot++;
    }
    var output = Mustache.to_html(node_template, this);
    console.log()
    document.getElementById('content').innerHTML+= output;
    var that = this;
    setTimeout(function(){
        for(var o in that.outputs){
            var out = that.outputs[o];
            var light = new toggle(out.type, that.name+out.type, out.index, out.display, out.state, that.name, rpc_on_off);                    
        }
        that.display_historical();
        that.display_day();
    }, 1000);
    this.init_video();
    var that = this;
    setInterval(function(){
        $.get("//"+url+"/graph/historical/"+that.name, function(data){
            that.historical = eval("("+data+")");
            that.display_historical();
        });
    }, 60000);
}

Node.prototype.init_video = function(){
    var that = this;
    document.getElementById(this.name+"_video_button").onclick = function(){
        document.getElementById(that.name+"_video").classList.add("video_overlay_show");
    }
    document.getElementById(this.name+"_video_close").onclick = function(){
        document.getElementById(that.name+"_video").classList.remove("video_overlay_show");
    }

}

Node.prototype.display_day = function(){            
    var that = this;
    var c = document.createElement("canvas");
    var prev = null;
    c.addEventListener('mousemove', function(e){                
        for(var i in that.nodes){
            var n = that.nodes[i];
            if(n.hit_test(e.offsetX, e.offsetY)){
                prev = n;
                $("#tooltip").remove();
                var start = parseInt(n.obj.start/60);
                var start_min = parseInt(n.obj.start%60);
                var end =  parseInt(n.obj.end/60);
                var end_min =  parseInt(n.obj.end%60);
                var st = n.obj.name+" "+zeroFill(start, 2)+":"+zeroFill(start_min, 2)+" - "+zeroFill(end, 2)+":"+zeroFill(end_min, 2);
                showTooltip(e.x, e.y, st);
                return;
            }else{
                $("#tooltip").remove();
            }
        }
    })
    var total_wid = $("#day_"+that.name).width();
    c.width = parseInt(total_wid);
    c.height = 40;            
    var wid = parseInt(total_wid)/1440;            
    function draw(){
        that.nodes = [];
        var rows = 0;
        var cxt =  c.getContext("2d");
        cxt.clearRect(0, 0, 575, 40);
        for(var re in that.repeaters){                    
            var r = that.repeaters[re];
            var pad = r.padding*wid;
            var p = new DayNode(0, 0, pad, daynode_height, "#dddddd");
            p.draw(c);
            var cur_wid=pad;
            for(var i=0; i<1440; i+=r.every){                        
                var w = wid*r.run_for;
                var on = new DayNode(cur_wid, rows*daynode_height, w, daynode_height, colors[rows], {name:r.output, start:i+r.padding, end:(i+r.padding)+r.run_for});
                on.draw(c);
                that.nodes.push(on);
                cur_wid+=w;
                var o_w = (r.every-r.run_for)*wid;
                var off = new DayNode(cur_wid, rows*daynode_height, o_w, daynode_height, "#dddddd");
                off.draw(c);
                cur_wid+=o_w;                        
            }
            rows++;
        }
        var ons = {};
        var ends = {};
        for(var cl in that.clocks){
            var clock = that.clocks[cl];
            if(clock.state_change == true){
                var t = clock.time[0]*60+clock.time[1];
                var cur = t+(offset/1000/60);
                cur = cur < 0 ? 1440+cur : cur;
                ons[clock.output] = [cur, clock.output]
            }else if(clock.state_change == false){
                var t = clock.time[0]*60+clock.time[1];
                var cur = t+(offset/1000/60);
                cur = cur < 0 ? 1440+cur : cur;
                ends[clock.output] = [cur, clock.output];
            }                    
        }

        for(var tt in ons){
            var o = ons[tt][0];
            var of = ends[tt][0];                    
            var w_on = wid*o;
            var w_off = wid*of;
            ob = {name:ons[tt][1], start:o, end:of};
            var on = new DayNode(w_on, rows*daynode_height, w_off-w_on, daynode_height, colors[rows], ob);
            on.draw(c);
            that.nodes.push(on);
            var off = new DayNode(0, rows*daynode_height, wid*o, daynode_height, "#dddddd");
            off.draw(c);
            var off2 = new DayNode(w_off, rows*daynode_height, 575-w_off, daynode_height, "#dddddd");
            off2.draw(c);
            rows++;
        }
        var now = new Date()
        var sec = now.getSeconds() ? (now.getSeconds()/60) : 0;
        now = (now.getHours()*60)+now.getMinutes()+sec;
        time = c.getContext("2d");
        time.fillStyle = "#333333";
        time.fillRect((now*wid), 0, 3, daynode_height*4);
        time.shadowColor = "#666666";
        time.shadowBlur = daynode_height/2;
        time.shadowOffsetX = 2;
        time.shadowOffsetY = 2;
        document.getElementById("day_"+that.name).appendChild(c);
    }
    setInterval(draw, 1000);
}

Node.prototype.display_historical = function(){
    var oldest = 999999999999999999999999999;
    var newest = 0;
    console.log(this.historical);
    for(var h in this.historical){
        try{
            var n = this.historical[h];
            if(n[3]){
                var da = new Date(n[0]).getTime()+offset;
                oldest = da < oldest ? da : oldest;
                newest = da > newest ? da : newest;                
                this.h_data[n[4]].data.push([da, n[3]]);
            }
        }catch(e){
            continue;
        }
    }
    var plots = [];
    for(var i in this.h_data){
        var p = this.h_data[i].data;
        try{
            p.push([newest, p[p.length-1][1]]);
            p.unshift([oldest, p[0][1]]);
        }catch(e){
            continue;
        }
        plots.push(this.h_data[i]);
    }
    console.log(plots);
    $.plot($("#historical_"+this.name), plots, {
        series: { lines: { show: true, fill: false},points:{show:true}},
        yaxis: { 
            min: 0,
            max: 100,
        },
        xaxis: {
            mode: "time",
            timeformat:"%H:%M:%S",
            minTickSize: [2, "hour"],
        },
        grid:{
            hoverable:true,
            color: "ffffff",
            backgroundColor: "eeeeee",
            borderWidth: 3,
            borderColor: "dddddd",
        }
    });
    this.enable_rollover();
}

function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

Node.prototype.enable_rollover = function(){
    var previousPoint = null;
    $("#historical_"+this.name).bind("plothover", function (event, pos, item) {
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

Node.prototype.update = function(){
    for(var d in this.sensors){
        var s = this.sensors[d];
        var n = [last_x, this.last[s.id]];
        this.data[s.id].push(n);
        this.data[s.id] = this.data[s.id].slice(-200);
        console.log(this.data[s.id].length);
    }
    this.display();
}

Node.prototype.display = function(){
    var plots = [];
    for (var d in this.data){
        this.prefs[d].data = this.data[d]
        plots.push(this.prefs[d]);
        document.getElementById(this.name+d+"_header").innerHTML = this.last[d].toFixed(2)+this.prefs[d].decorator;
    }
    console.log(plots);
    $.plot($("#"+this.name), plots, {
        series: { lines: { show: true, fill: false},},
        yaxis: { 
            min: 0,
            max: 100,
        },
        xaxis: {
            mode: "time",
            timeformat:"%H:%M:%S",
            minTickSize: [5, "second"],
        },
        grid:{
            color: "ffffff",
            backgroundColor: "eeeeee",
            borderWidth: 3,
            borderColor: "dddddd",
        }
    });
}
