var radius = window.innerHeight;

var tree = d3.layout.tree()
    .size([360, radius - 120])
    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

var diagonal = d3.svg.diagonal.radial()
    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var vis = d3.select("#chart").append("svg")
    .attr("width", radius * 2)
    .attr("height", radius * 2 - 150)
    .append("g")
    .attr("transform", "translate(" + radius + "," + radius + ")");

d3.json("tree", function(json) {
    var nodes = tree.nodes(json);

    var link = vis.selectAll("path.link")
        .data(tree.links(nodes))
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("d", diagonal);

    var node = vis.selectAll("g.node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
        .style("stroke", color)

    node.append("circle")
        .attr("r", 4.5);
    /*
    node.append("text")
        .attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
        .attr("dy", ".31em")
        .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
        .attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })
        .text(function(d) { return d.type; });
    */

    document.getElementById("notification").innerHTML = ""
});

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