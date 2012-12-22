Applications.Node = function(){
    this.inter = false;
    this.node_objs = {};
    this.graph = false;
    this.node_template = "";
    this.historical = {};
}

Applications.Node.prototype = new App();
Applications.Node.constructor = Applications.Node;

Applications.Node.prototype.update_toggle = function(frame){
    var tog = document.getElementById(frame.node+frame.type);
    tog.obj.set_state(frame.state);
}

Applications.Node.prototype.update_input = function(frame){
    var tog = document.getElementById(frame.node+frame.type);
    if(frame.value){
        tog.children[1].classList.add('on');
    }else{
        tog.children[1].classList.remove('on');
    }
}

Applications.Node.prototype.init = function(){
    for(var n in loc.nodes){
        var node = loc.nodes[n];
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

    this.graph.onmessage = function(e){
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

Applications.Node.prototype.run = function(){
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

Applications.Node.prototype.stop = function(){
    clearInterval(this.inter);
};

window.onresize = function(ev){
    for(var n in this.app.node_objs){
        this.app.node_objs[n].display_day();
    }
}

window.application = Applications.Node;

