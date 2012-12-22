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
            s.decorator = decorators[s.type];
            this.prefs[s.id] = {color:colors[tot], decorator:decorators[s.type]}
            this.last[s.id] = s.value;
            this.data[s.id] = [];
            this.h_data[s.id] = {data:[], color:colors[tot]};
            tot++;
        }
    }
    var template = document.getElementById('dashboard_template').innerHTML;
    var output = Mustache.to_html(template, {nodes:loc.nodes});
    document.getElementById('content').innerHTML+= output;
}

Applications.Dashboard.prototype.run = function(){}
Applications.Dashboard.prototype.stop = function(){}

window.application = Applications.Dashboard;