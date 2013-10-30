// set up SVG for D3
var mode = "design";
//var width  = 620,
 //   height = 300,
 //   colors = d3.scale.category10();

var width  = $("#width").text(),
    height = $("#height").text(),
    colors = d3.scale.category10();

var svg = d3.select('.topology')
  .append('svg')
  .attr('width', width)
  .attr('height', height);
var board = svg.append('svg:g')
    .call(d3.behavior.zoom().on("zoom", rescale))
    .on("dblclick.zoom", null)
  .append('svg:g')
    .on("mousemove", mousemove)
    .on("mousedown", mousedown)
    .on("mouseup", mouseup);
    
var tooltip = CustomTooltip( "posts_tooltip", 240 );

var bandwidth_capacities = ['10M', '100M', '1G', '10G'];
var gre_ovs_capacity = [];


board.append('svg:rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'white');

function rescale() {
    
  if(d3.event.ctrlKey || mousedown_node || mousedown_link || mousedown_icon) return;
  trans=d3.event.translate;
  scale=d3.event.scale;

  board.attr("transform",
      "translate(" + trans + ")"
      + " scale(" + scale + ")");
}
var icon_data = [
    {
        x: 30, y: 100, icon: 'img/floodlight.png', 
        type: 'controller', name: '控制器', count:0,
        allows:{'fv': true},
        type_id: 1,
        required: true,
        limit: 1
    },
    {
        x: 30, y: 150, icon: 'img/flowvisor.png', 
        type: 'fv', name: 'FV', count:0,
        allows:{'switch': true, 'controller': true},
        type_id: 2,
        required: true,
        limit: 1
    },
    {
        x: -20, y: -20, icon: 'img/switch1.png', 
        type: 'switch', name: '交换机', count: 0, 
        type_id: 3,
        width: 40, height:40,
        allows: {'host':true, 'switch': true, 'fv': true}
    },
    {
        x: -15, y: -15, icon: 'img/host1.png', 
        type: 'host', name: '主机', count:0,
        type_id: 4,
        width: 30, height:30,
        allows:{'switch': true, 'vm': true}
    },
    {
        x: 30, y: 300, icon: 'static/img/vm.png', 
        type: 'vm', name: '虚拟机', count:0,
        type_id: 5,
        allows:{'host': true}
    }
];
var color_map = {'switch': 2, 'host': 1, 'vm':3, 'fv':4, 'controller':5};
var vm_state = {
    0: 'nostate',
    1: "running",
    3: "blocked",
    4: "paused",
    5: "shutdown",
    6: "shutoff",
    7: "crashed",
    8: "pmsuspended",
    9: "building",
    10: "failed",
    11: "notexist",
}
var server = '/';
var static_url = $("#STATIC_URL").text();
var create_node = function(d, point, trigger) {
      // insert new node at point
      var node = {id: ++lastNodeId, reflexive: false};
      if (point) {
          node.x = point[0];
          node.y = point[1];
      }
      d.count ++;
      //if (d.limit <= 0) {
      //    return;
      //}
      d.limit --;
      if (d.limit <= 0 && trigger) {
          trigger.style('opacity', '0.2');
      }
      node.type = d.type;
      node.count = d.count;
      node.name = d.name;
      node.allows = d.allows;
      node.required = d.required;
      node.icon = d.icon;
      node.width = d.width;
      node.height = d.height;
      node.x = d.x;
      node.y = d.y;
      //node.have_port = false;
      if (node.type == 'vm') {
        node.limit = 1;    
      }
      if (node.type == 'host') {
        node.max = 5;    
      }
      nodes_data.push(node);
      return node;
};
var mousedown_icon = null;

// set up initial nodes and links
//  - nodes are known by 'id', not by index in array.
//  - reflexive edges are indicated on the node (as a bold black circle).
//  - links are always source < target; edge directions are set by 'left' and 'right'.
var nodes_data = [],
  lastNodeId = 0;

var switches = new Array(),
    normals = new Array(),
    srcLinks = new Array(),
    links = [];
//var first_controller = create_node(icon_data[0], null, d3.select('.controller-node-icon'));
//var first_fv = create_node(icon_data[1], null, d3.select('.fv-node-icon'));
//var first_switch = create_node(icon_data[2]);
//var first_switch = create_node(icon_data[2]);
//var first_switch = create_node(icon_data[2]);
//var first_host = create_node(icon_data[3]);
//first_host.required = true;
//first_switch.required = true;

//var links = [
//    {source: nodes_data[0], target: nodes_data[1], left: false, right: true, required: true },
//    {source: nodes_data[1], target: nodes_data[2], left: false, right: true, required: true },
//    {source: nodes_data[2], target: nodes_data[3], left: false, right: true, required: true },
//];

function get_node(key){
    for(var i=0; i< nodes_data.length; i++){
        if(nodes_data[i].key == key){
            return nodes_data[i].id;
        }
    }
    return;
}

function inittpdata(){
    //获取数据库中该slice的拓扑信息 
    var slice_id = $("#slice_id").text();
    var topology_url = "http://" + window.location.host + "/slice/topology/"+slice_id+"/";
    $.ajax({
        type: "GET",
        url: topology_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
            switches = data.switches;
            srcLinks = data.links;
            normals = data.normals;
            //获取数据库中该slice的交换机信息
            for(var i=0; i< switches.length; i++){
                icon_data[2].key = switches[i].dpid;
                
                node = create_node(icon_data[2]);
                if(node){
                    nodes_data[node.id-1].key = switches[i].dpid;
                    nodes_data[node.id-1].yid = switches[i].id;
                    nodes_data[node.id-1].name = switches[i].name;
                    nodes_data[node.id-1].type_id = switches[i].type;
                    nodes_data[node.id-1].ports = switches[i].ports;
                    if(switches[i].type == 1){
                        nodes_data[node.id-1].icon = 'img/ovs.png';
                    }else if(switches[i].type == 2){
                        nodes_data[node.id-1].icon = 'img/ovs-red.png';
                    }else{
                        nodes_data[node.id-1].icon = 'img/ovs-green.png';
                    }
                }
            }
            //获取数据库中该slice的交换机的连接信息
            for (var i = 0; i < srcLinks.length; i++) {
                gre_ovs_capacity.push(bandwidth_capacities[Math.floor(Math.random() * 4)]);
            };
            var flag = true;
            for(var i=0; i< srcLinks.length; i++){
                flag = true;
                for(var j=0; j< i; j++){
                    if((srcLinks[i].src_switch == srcLinks[j].src_switch && srcLinks[i].dst_switch == srcLinks[j].dst_switch)||
                        (srcLinks[i].src_switch == srcLinks[j].dst_switch && srcLinks[i].dst_switch == srcLinks[j].src_switch)){
                        flag = false;
                        break;
                    }
                }
                if(flag){
                    src_node_id = get_node(srcLinks[i].src_switch);
                    dst_node_id = get_node(srcLinks[i].dst_switch);
                    //nodes_data[src_node_id-1].have_port = true;
                    //nodes_data[dst_node_id-1].have_port = true;
                    if(src_node_id && dst_node_id){
                        link = {source: nodes_data[src_node_id-1], target: nodes_data[dst_node_id-1], src_port_name: srcLinks[i].src_port_name,
                            src_port: srcLinks[i].src_port, dst_port_name: srcLinks[i].dst_port_name,
                            dst_port: srcLinks[i].dst_port, right: true, required: true, type: 'switchswitch',
                            capacity: gre_ovs_capacity[i]};
                        links.push(link);
                    }
                 }
            }
            //获取数据库中该slice的主机信息
            for(var i=0; i< normals.length; i++){
               
                src_node = create_node(icon_data[3]);
                dst_node_id = get_node(normals[i].switchDPID);
                if(src_node && dst_node_id){
                    nodes_data[src_node.id - 1].key = normals[i].ip;
                    nodes_data[src_node.id - 1].yid = normals[i].hostid;
                    nodes_data[src_node.id - 1].type_id = normals[i].hostStatus;
                    nodes_data[src_node.id - 1].name = normals[i].name;
                    nodes_data[src_node.id - 1].mac = normals[i].mac;
                   // nodes_data[src_node.id - 1].vnc_port = normals[i].vnc_port;
                    if(normals[i].hostStatus == 1){
                        nodes_data[src_node.id - 1].icon = 'img/host.png';
                    }else{
                        nodes_data[src_node.id - 1].icon = 'img/host_down.png';
                    }
                    link = {source: nodes_data[src_node.id - 1], target: nodes_data[dst_node_id-1], left: false,
                        right: true, required: true, type: 'hostswitch'};
                    links.push(link);
                }
            }     
        }
    });
}

inittpdata();

// init D3 force layout
var force = d3.layout.force()
    .nodes(nodes_data)
    .links(links)
    .size([width, height])
    .linkDistance(function(d){
            var distance = 50;
            if (d.type == 'switchswitch') {
                distance = 100;
            }
            return distance;
        })
    .charge(-500)
    .on('tick', tick)

// line displayed when dragging new nodes
var drag_line = board.append('svg:path')
  .attr('class', 'link dragline hidden')
  .attr('d', 'M0,0L0,0');

// handles to link and node element groups
var path = board.append('svg:g').selectAll('g'),
    circle = board.append('svg:g').selectAll('g');

// mouse event vars
var selected_node = null,
    selected_link = null,
    mousedown_link = null,
    mousedown_node = null,
    mouseup_node = null;

function resetMouseVars() {
  mousedown_node = null;
  mouseup_node = null;
  mousedown_link = null;
}

// update force layout (called automatically each iteration)
function tick() {
  // draw directed edges with proper padding from node centers
  var ph = path.selectAll('.link');
  ph.attr('d', function(d) {
    var deltaX = d.target.x - d.source.x,
        deltaY = d.target.y - d.source.y,
        dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
        normX = deltaX / dist,
        normY = deltaY / dist,
        sourcePadding = d.left ? 17 : 12,
        targetPadding = d.right ? 17 : 12,
        sourceX = d.source.x + (sourcePadding * normX),
        sourceY = d.source.y + (sourcePadding * normY),
        targetX = d.target.x - (targetPadding * normX),
        targetY = d.target.y - (targetPadding * normY);
    return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
  });

  circle.attr('transform', function(d) {
    return 'translate(' + d.x + ',' + d.y + ')';
  });
}

function highlight( data, element ) {
    //d3.select( element ).attr( "stroke", "black" );
    var content = "";
    //alert(data.type);
    if (data.type == 'switch') {
        content += "<h6>dpid：" + data.key + "</h6>";
        if(data.ports){
            content += "<table class='table'>" + 
            "<tr><th>端口</th>" + 
            "</tr>";
            //alert(data.ports[0].name);
            for (var i = 0; i < data.ports.length; i++) {
                flag = false;
                for (var j = 0; j < links.length; j++) {
                    if(links[j].source.id == data.id && links[j].target.type == 'switch' && links[j].src_port_name == data.ports[i].name && links[j].src_port == data.ports[i].port){
                        content += "<tr><td>"; 
                        content += links[j].source.name + ":" + links[j].src_port_name + "(" + links[j].src_port+ ")";
                        content += ' <-----> ' + links[j].target.name + ":" + links[j].dst_port_name + "(" + links[j].dst_port + ")";
                        content += "</td></tr>";
                        flag = true;
                        break;
                    }else if(links[j].target.id == data.id && links[j].source.type == 'switch' && links[j].dst_port_name == data.ports[i].name && links[j].dst_port == data.ports[i].port){
                        content += "<tr><td>"; 
                        content += links[j].target.name + ":" + links[j].dst_port_name + "(" + links[j].dst_port+ ")";
                        content += ' <-----> ' + links[j].source.name + ":" + links[j].src_port_name + "(" + links[j].src_port + ")";
                        content += "</td></tr>";
                        flag = true;
                        break;
                    }
                } 
                if(!flag){
                    content += "<tr><td>"; 
                    content += data.name + ":" + data.ports[i].name + "(" + data.ports[i].port+ ")";
                    content += "</td></tr>";
                }
            }
            content += "</table>";
        }
        tooltip.showTooltip(content, d3.event);
   }else if(data.type == 'host'){
        content += "<h6>ip：" + data.key + "</h6>";
        content += "<table class='table'>" + 
            "<tr><th>状态</th>" + 
            "<th>MAC地址</th></tr>";

        content += "<tr>" + 
            "<td>" + vm_state[data.type_id] + "</td>" + 
            "<td>" + data.mac + "</td>" + 
            "</tr>";

        content += "</table>";
        tooltip.showTooltip(content, d3.event);
   }else if(data.type == 'switchswitch'){
        content += "<h6>带宽使用：" + data.bandwidth + data.capacity.slice(data.capacity.length - 1) + "/" + data.capacity + "</h6>";
        content += "<table class='table'>" + 
            "<tr><th>端口</th></tr>";
        content += "<tr><td>"; 
        content += data.source.name + ":" + data.src_port_name + "(" + data.src_port+ ")";
        content += ' <-----> ' + data.target.name + ":" + data.dst_port_name + "(" + data.dst_port + ")";
        content += "</td></tr></table>";
        tooltip.showTooltip(content, d3.event);
        //} else if (data.bandwidth) {
        //    content += "带宽使用：" + data.bandwidth + data.capacity.slice(data.capacity.length - 1) + "/" + data.capacity;
        //   tooltip.showTooltip(content, d3.event);
        //}
    }
}


// update graph (called when needed)
function restart() {
  // path (link) group
  path = path.data(links);

  // update existing links
  path.selectAll('.link')
     .classed('selected', function(d) { return d === selected_link; })
  //  .style('marker-start', function(d) { return d.left ? 'url(#start-arrow)' : ''; })
  //  .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; });


  // add new links
  var g = path.enter().append('svg:g');
  g.append('svg:path')
    .attr("class", "link")
    .style("stroke-width", function (d) { 
        var width = 1;
        if (d.type == 'switchswitch') {
            width = 2;
        }
        return width; 
    })
    .style("stroke", function (d) { 
        var color = 'black';
        
        if (d.type == 'switchswitch') {
            var rand_num = Math.random();
            var bandwidth = rand_num * parseInt(d.capacity.slice(0, d.capacity.length - 1));
            d.bandwidth = bandwidth.toFixed(2);
            if (rand_num < 0.3) {
                color = 'green';   
            } else if (rand_num < 0.6) {
                color = 'yellow';
            } else if (rand_num < 0.9) {
                color = 'orange';
            } else {
                color = 'red';
            }
        }
        return color; 
    })
    .attr('id', function(d){ return d.source.id + " " + d.target.id})
    .on('mouseover', function(d) {
        highlight( d, this );
    });
   // .on('mouseout', function(d, i) {
   //     tooltip.hideTooltip();
   // });
 
 //g.append('svg:text')
  //  .attr("dx", 30)
  //  .attr("dy", 10)
  //  .attr('fill', '#000')
  //  .append("svg:textPath")
  //  .attr("xlink:href", function(d){ return "#" + d.source.id + " " + d.target.id})
    //.text(function(d) { return "sasaggggg"});
    

  // remove old links
  path.exit().remove();

  // circle (node) group
  // NB: the function arg is crucial here! nodes are known by id, not by index!
  circle = circle.data(nodes_data, function(d) { return d.id; });

  // update existing nodes (reflexive & selected visual states)
  circle.selectAll('.node')
  //  .style('fill', function(d) { return (d === selected_node) ? d3.rgb(colors(color_map[d.type])).brighter().toString() : colors(color_map[d.type]); })
    .classed('reflexive', function(d) { return d.reflexive; });

  // add new nodes
  var g = circle.enter().append('svg:g');
  g.append('svg:image')
    .attr("xlink:href", function(d){ return static_url + d.icon})
    .attr("target", "_blank")
    .attr('x', function(d){ return d.x; })
    .attr('y', function(d){ return d.y; })
    .attr('width', function(d){ return d.width; })
    .attr('height', function(d){ return d.height; })
    .attr('class', function(d) {return 'node node-icon ' + d.type + '-node-icon'})
   // .attr('class', 'node bootstro bootstro-highlight')
   // .attr('data-bootstro-title', 'asdasdasasdas')
   // .attr('r', 25)
   // .style('fill', function(d) { return (d === selected_node) ? d3.rgb(colors(color_map[d.type])).brighter().toString() : colors(color_map[d.type]); })
   // .style('stroke', function(d) { return d3.rgb(colors(color_map[d.type])).darker().toString(); })
    //.classed('reflexive', function(d) { return d.reflexive; })
    .on('click', function(d) {
        if(d.type == 'switch'){
            window.top.location.href = "http://" + window.location.host + "/monitor/Switch/"+d.yid+"/";
        }else{
            window.top.location.href = "http://" + window.location.host + "/monitor/vm/"+d.yid+"/";
        }  
    })
    .on('mouseover', function(d) {
        highlight( d, this );
    })
     .on('mouseout', function(d, i) {
        tooltip.hideTooltip();
    })
    .on('mousedown', function(d) {
      if(d3.event.ctrlKey) return;
        board.call(d3.behavior.zoom().on("zoom", null))

      // select node
      mousedown_node = d;
      if(mousedown_node === selected_node) selected_node = null;
      else selected_node = mousedown_node;
      selected_link = null;

      // reposition drag line
      drag_line
        .style('marker-end', 'url(#end-arrow)')
        .classed('hidden', false)
        .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y);

      restart();
    })
    .on('mouseup', function(d) {
      if(!mousedown_node) return;
        board.call(d3.behavior.zoom().on("zoom", rescale))

      // needed by FF
      drag_line
        .classed('hidden', true)
        .style('marker-end', '');

      // check for drag-to-self
      mouseup_node = d;
      if(mouseup_node === mousedown_node) { resetMouseVars(); return; }

      // unenlarge target node
      d3.select(this).attr('transform', '');

      // add link to graph (update if exists)
      // NB: links are strictly source < target; arrows separately specified by booleans
      var source, target, direction;
      if(mousedown_node.id < mouseup_node.id) {
        source = mousedown_node;
        target = mouseup_node;
        direction = 'right';
      } else {
        source = mouseup_node;
        target = mousedown_node;
        direction = 'left';
      }

      var pair = source.type + target.type;
      if (pair == 'hostvm' || pair == 'vmhost') {
          for (var i = 0; i < [source, target].length; i++) {
              var current_node = [source, target][i];
              if (current_node.max) {
                if (current_node.max <= 1) {
                    return;
                } else {
                    current_node.max --;
                }
              }
          };
      }
      /* only accept allowed node */
      
      if (!(target.type in source.allows)) {
         return;
      }
      if (source.limit <= 0) {
          return;
      }
      source.limit --;
      if (target.limit <= 0) {
          return;
      }
      target.limit --;
      var link;
      link = links.filter(function(l) {
        return (l.source === source && l.target === target);
      })[0];

      if(link) {
        link[direction] = true;
      } else {
        link = {source: source, target: target, left: false, right: false};
        link[direction] = true;
        links.push(link);
      }

      // select new link
      selected_link = link;
      selected_node = null;
      restart();
    });

  // show node IDs
  g.append('svg:text')
      .attr('x', function(d) { return d.width / 2 - d.x + 5; })
      .attr('y', 4)
      .attr('class', 'id')
      .attr('fill', '#000')
      .text(function(d) { return d.name; });

  // remove old nodes
  circle.exit().remove();

  // set the graph in motion
  force.start();
}

function mousedown() {
  // prevent I-bar on drag
  //d3.event.preventDefault();
  
  // because :active only works in WebKit?
  board.classed('active', true);

  if(d3.event.ctrlKey || mousedown_node || mousedown_link || mousedown_icon) return;

    board.call(d3.behavior.zoom().on("zoom", rescale))

  // insert new node at point
/*
  var point = d3.mouse(this),
      node = {id: ++lastNodeId, reflexive: false};
  node.x = point[0];
  node.y = point[1];
  nodes_data.push(node);

  restart();
*/
}

function mousemove() {
  if(!mousedown_node) return;

  // update drag line
  //drag_line.attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + d3.mouse(this)[0] + ',' + d3.mouse(this)[1]);
  mousedown_node.x = d3.mouse(this)[0] ;
  mousedown_node.y = d3.mouse(this)[1];
  restart();
}

function mouseup() {
  if(mousedown_node) {
    // hide drag line
    drag_line
      .classed('hidden', true)
      .style('marker-end', '');
  }

  // because :active only works in WebKit?
  board.classed('active', false);

  // clear mouse event vars
  resetMouseVars();
}
restart();

var refresh_time = 10000;

function random_refresh () {
    setTimeout(function  () {
        //alert('in');
        refresh_time = Math.floor(Math.random() * 10000 + 2000 );
        var ph = path.selectAll('.link');
          ph.style("stroke", function (d) { 
            var color = 'black';
            
            if (d.type == 'switchswitch') {
                var rand_num = Math.random();
                var bandwidth = rand_num * parseInt(d.capacity.slice(0, d.capacity.length - 1));
                d.bandwidth = bandwidth.toFixed(2);
                if (rand_num < 0.3) {
                    color = 'green';   
                } else if (rand_num < 0.6) {
                    color = 'yellow';
                } else if (rand_num < 0.9) {
                    color = 'orange';
                } else {
                    color = 'red';
                }
            }
            return color; 
        });
        random_refresh();
    }, refresh_time);
}
random_refresh();
