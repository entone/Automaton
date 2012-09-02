var h = window.innerHeight,
    w = window.innerWidth,
    root,
    fill = d3.scale.category20();

var vis = d3.select("#chart").append("svg:svg")
    .attr("width", w)
    .attr("height", h);



d3.json("tree", function(json) {
  root = json;
  update();
});

var force  = false;

function update(){
    document.getElementById("notification").innerHTML = "Rendering..."
    var tree = d3.layout.tree()
    var nodes = tree.nodes(root);
    var links = tree.links(nodes);

    var k = Math.sqrt(nodes.length / (w * h));

    force = force ? force : d3.layout.force()
        .charge(-10/k)
        .gravity(100*k)
        .nodes(nodes)
        .links(links)
        .size([w, h])
        .start();

    var link = vis.selectAll("line.link")
        .data(links)
        .enter()
        .append("svg:line")
        .style("stroke", "#666666")
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    var node = vis.selectAll("circle.node")
        .data(nodes)
        .enter()
        .append("svg:circle")
        .style("fill", color)
        .style("stroke", "#666666")
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
        .attr("r", weight)        
        .call(force.drag);

    force.on("tick", function() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
    });
    document.getElementById("notification").innerHTML = ""
}

function color(d){
    switch(d.type){
        case 'share':
            return "#CCCCCC";
            break;
        case 'donate':
            return "#C4C065";
            break;
        case 'rsvp':
            return "#1E9E9D";
            break;
        case 'like':
            return "#FB8B25";
            break;
        case 'signup':
            return "#CC5481";
            break;
        case 'progress':
            return "#999999";
            break;
        case 'clickback':
            return "#333333";
            break;
        default:
            return "#000000";
    }
}

function weight(d) {
    if(d.amount) return d.amount/5
  return d.children.length ? d.children.length > 10 ? 10 : d.children.length : 4.5; 
}