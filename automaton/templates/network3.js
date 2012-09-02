var width = window.innerWidth,
    height = 5000;

var cluster = d3.layout.cluster()
    .size([height, width - 160]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var vis = d3.select("#chart").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(40, 0)");

d3.json("tree", function(json) {
  var nodes = cluster.nodes(json);

  var link = vis.selectAll("path.link")
      .data(cluster.links(nodes))
    .enter().append("path")
      .attr("class", "link")
      .attr("d", diagonal);

  var node = vis.selectAll("g.node")
      .data(nodes)
    .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })

  node.append("circle")
      .attr("r", weight)
      .style("stroke", color);


  node.append("text")
      .attr("dx", function(d) { return d.children ? -8 : 8; })
      .attr("dy", 3)
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d) { return d.type; });

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