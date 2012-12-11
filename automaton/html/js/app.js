function zeroFill(number, width){
    width -= number.toString().length;
    if (width > 0){
        return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
    }
    return number + ""; // always return a string
}
var colors = ["#80DE03", "#C53437", "#6FDDFC", "#1D8480", "#E25618"];
var decorators = {ph: "", temperature:"&deg;C",humidity:"%",light:"%", etape:"cm", ec:"ppm", dissolved_oxygen:"ppm"}
var offset = -(new Date().getTimezoneOffset()*60*1000);    
var last_x = new Date().getTime()+offset;
var daynode_height = 10;

App = function(){
    this.inter = false;
    this.node_objs = {};
    this.graph = false;
    this.node_template = "";
    this.historical = {};
}

function rpc_on_off(obj){
    console.log("Setting:");
    obj = {node:obj.node, index:obj.index, state:obj.on};
    console.log(obj);
    $.post("//"+url+"/rpc/", JSON.stringify(obj), function(res){
        console.log(eval("("+res+")"));
    });
}

App.prototype.update_toggle = function(frame){
    var tog = document.getElementById(frame.node+frame.type);
    tog.obj.set_state(frame.state);
}

App.prototype.update_input = function(frame){
    console.log(frame);
    var tog = document.getElementById(frame.node+frame.type);
    if(frame.value){
        tog.children[1].classList.add('on');
    }else{
        tog.children[1].classList.remove('on');
    }
}

App.prototype.init = function(){
    for(var n in nodes){
        var node = nodes[n];
        console.log("Creating Node:");
        console.log(node);
        var new_node = new Node(node);
        this.node_objs[new_node.name] = new_node;
    }

    this.run();
    
    this.graph = new WebSocket("ws://"+url+"/graph/");    
    var that = this;
    
    this.graph.onopen = function() {
        console.log("Graph OPEN");
        this.send('hi');
    };

    this.graph.onmessage = function(e) {
        var lines = e.data.split('\n');
        for (var i = 0; i < lines.length - 1; i++) {
            var frame = eval("("+lines[i]+")");
            switch(frame.cls){
                case 'Output':
                    that.update_toggle(frame);
                    break;
                case 'Input':
                    that.update_input(frame);
                    break;
                default:
                    var node = that.node_objs[frame.node];
                    node.last[frame.id] = frame.value;
                    break;
            }
        }
        this.send('');
    };
}

App.prototype.run = function(){
    for(var i in this.node_objs){
        for(var d in this.node_objs[i].data){
            this.node_objs[i].data[d] = [];
        }                    
    }
    var that = this;
    this.inter = setInterval(function(){
        last_x = new Date().getTime()+offset;
        for(var i in that.node_objs){
            that.node_objs[i].update();
        }
    }, 150);
};

App.prototype.stop = function(){
    clearInterval(this.inter);
};

window.onload = function(){    
    this.app = new App();
    this.app.init();
};

window.onblur = function(){
    this.app.stop();
};
