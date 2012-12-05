var inter = false;
var offset = -(new Date().getTimezoneOffset()*60*1000);
var last_x = new Date().getTime()+offset;       
var node_objs = {};
var graph = false;
var node_template = "";
var colors = ["#80DE03", "#C53437", "#6FDDFC", "#1D8480", "#E25618"];
var decorators = {ph: "", temperature:"&deg;C",humidity:"%",light:"%", etape:"cm", ec:"ppm", dissolved_oxygen:"ppm"}
var historical = {};
var daynode_height = 10;

function zeroFill(number, width){
    width -= number.toString().length;
    if (width > 0){
        return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
    }
    return number + ""; // always return a string
}

function rpc_on_off(obj){
    console.log("Setting:");
    obj = {node:obj.node, index:obj.index, state:obj.on};
    console.log(obj);
    $.post("//"+url+"/rpc/", JSON.stringify(obj), function(res){
        console.log(eval("("+res+")"));
    });
}

function update_toggle(frame){
    var tog = document.getElementById(frame.node+frame.type);
    tog.obj.set_state(frame.state);
}

function update_input(frame){
    console.log(frame);
    var tog = document.getElementById(frame.node+frame.type);
    if(frame.value){
        tog.children[1].classList.add('on');
    }else{
        tog.children[1].classList.remove('on');
    }
}

function init(){
    graph = new WebSocket("ws://"+url+"/graph/");
    node_template = document.getElementById('node_template').innerHTML;
    
    graph.onopen = function() {
        console.log("Graph OPEN");
        graph.send('hi');
    };

    graph.onmessage = function(e) {
        var lines = e.data.split('\n');
        for (var i = 0; i < lines.length - 1; i++) {
            var frame = eval("("+lines[i]+")");
            switch(frame.cls){
                case 'Output':
                    update_toggle(frame);
                    break;
                case 'Input':
                    update_input(frame);
                    break;
                default:
                    var node = node_objs[frame.node];
                    node.last[frame.id] = frame.value;
                    break;
            }
        }
        this.send('');
    };

    for(var n in nodes){
        var node = nodes[n];
        console.log("Creating Node:");
        console.log(node);
        var new_node = new Node(node);
        node_objs[new_node.name] = new_node;
    }

    run();
}

function run(){
    for(var i in node_objs){
        for(var d in node_objs[i].data){
            node_objs[i].data[d] = [];
        }                    
    }
    inter = setInterval(function(){
        last_x = new Date().getTime()+offset;
        for(var i in node_objs){
            node_objs[i].update();
        }
    }, 150);
}

function stop(){
    clearInterval(inter);
}

window.onload = function() {
    init();
}

window.onfocus = function(){
    run();
}

window.onblur = function(){
    stop();
}