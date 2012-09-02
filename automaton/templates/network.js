var w = window.innerWidth,h = window.innerHeight,node,link,root,colorscale = d3.scale.category10();

var force = d3.layout.force()
    .on("tick", tick)
    .charge(function(d) { return d._children ? -d.size : -30; })
    .linkDistance(function(d) { return d.target._children ? 80 : 30; })
    .size([w, h]);

var vis = d3.select("#chart").append("svg")
    .attr("width", w)
    .attr("height", h);

d3.json("tree", function(json) {
  root = json;
  //root.fixed = true;
  root.x = w / 2;
  root.y = h / 2;
  update();
});

function update() {
    var tree = d3.layout.tree()
    var nodes = tree.nodes(root);
    var links = tree.links(nodes);

  // Restart the force layout.

  force
      .nodes(nodes)
      .links(links)
      .start();

  // Update the links…
  link = vis.selectAll("line.link")
      .data(links, function(d) { return d.target.id; });

  // Enter any new links.
  link.enter().insert("line", ".node")
      .attr("class", "link")
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  // Exit any old links.
  link.exit().remove();

  // Update the nodes…
  node = vis.selectAll("circle.node")
      .data(nodes, function(d) { return d.id; })
      .style("fill", color);
  node.transition()
      .attr("r", function(d) { return d.children.length ? d.children.length : 4.5; });
  // Enter any new nodes.
  node.enter().append("circle")
      .attr("class", "node")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", function(d) { return d.children.length ? d.children.length : 4.5; })
      .style("fill", color)
      .on("click", click)
      .call(force.drag);

  node.append("title")
      .text(function(d) { return d._id; });

  // Exit any old nodes.
  node.exit().remove();
  document.getElementById("notification").innerHTML = ""

}

function separation(a, b) {
  return (a.parent == b.parent ? 1 : 2) / a.depth;
}

function tick() {
  link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  node.attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });
}

// Color leaf nodes orange, and packages white or blue.
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

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update();
}

// Returns a list of all nodes under the root.
function flatten(root) {
  var nodes = [], i = 0;

  function recurse(node) {
    if (node.children) node.size = node.children.reduce(function(p, v) { return p + recurse(v); }, 0);
    if (!node.id) node.id = ++i;
    nodes.push(node);
    return node.size;
  }

  root.size = recurse(root);
  return nodes;
}