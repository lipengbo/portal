// set up SVG for D3

function initboard(){
    var checkband = $("#checkband").text();
    if(checkband == 1){
        $("div#topology_top").empty();
        var str = "";
        str = str + "<svg id='svgc' width='100%' height='100%' version='1.1' xmlns='http://www.w3.org/2000/svg'>";
        str = str + "<text style=\"fill:black;font-size:10pt\" x='0' y='15'>无负载信息</text>";
        str = str + "<line x1='70' y1='10' x2='90' y2='10' style=\"stroke:black;stroke-width:2\"/>";
        str = str + "<text style=\"fill:black;font-size:10pt\" x='0' y='35'>0~30</text>";
        str = str + "<line x1='40' y1='30' x2='60' y2='30' style=\"stroke:green;stroke-width:2\"/>";
        str = str + "<text style=\"fill:black;font-size:10pt\" x='70' y='35'>30~60</text>";
        str = str + "<line x1='115' y1='30' x2='135' y2='30' style=\"stroke:yellow;stroke-width:2\"/>";
        str = str + "<text style=\"fill:black;font-size:10pt\" x='0' y='50'>60~90</text>";
        str = str + "<line x1='40' y1='45' x2='60' y2='45' style=\"stroke:orange;stroke-width:2\"/>";
        str = str + "<text style=\"fill:black;font-size:10pt\" x='70' y='50'>90~100</text>";
        str = str + "<line x1='115' y1='45' x2='135' y2='45' style=\"stroke:red;stroke-width:2\"/>";
        str = str + "</svg>";
        $("div#topology_top").append(str);
    }
}
function initboard2(){
    var top = $("#top").text();
    if(top == 1){
        svg.append('svg:text')
          .attr('x', 0)
          .attr('y', 15)
          .attr('style', "fill:black;font-size:8pt")
          .text("链路负载(%)");
        svg.append('svg:text')
          .attr('x', 0)
          .attr('y', 35)
          .attr('style', "fill:black;font-size:8pt")
          .text("0~30");
        svg.append('svg:line')
          .attr('x1', 40)
          .attr('y1', 30)
          .attr('x2', 60)
          .attr('y2', 30)
          .attr('style', "stroke:green;stroke-width:2")
        svg.append('svg:text')
          .attr('x', 70)
          .attr('y', 35)
          .attr('style', "fill:black;font-size:8pt")
          .text("30~60");
        svg.append('svg:line')
          .attr('x1', 115)
          .attr('y1', 30)
          .attr('x2', 135)
          .attr('y2', 30)
          .attr('style', "stroke:yellow;stroke-width:2")
        svg.append('svg:text')
          .attr('x', 0)
          .attr('y', 50)
          .attr('style', "fill:black;font-size:8pt")
          .text("60~90");
        svg.append('svg:line')
          .attr('x1', 40)
          .attr('y1', 45)
          .attr('x2', 60)
          .attr('y2', 45)
          .attr('style', "stroke:orange;stroke-width:2")
        svg.append('svg:text')
          .attr('x', 70)
          .attr('y', 50)
          .attr('style', "fill:black;font-size:8pt")
          .text("90~100");
        svg.append('svg:line')
          .attr('x1', 115)
          .attr('y1', 45)
          .attr('x2', 135)
          .attr('y2', 45)
          .attr('style', "stroke:red;stroke-width:2")
   //    svg.append('svg:rect')
   //       .attr('x', 200)
   //       .attr('y', 45)
   //       .attr('rx', 15)
   //       .attr('ry', 15)
   //       .attr('width', 100)
   //       .attr('height', 30)
   //       .attr('style', "fill:red;stroke:black;")
   //       .on('click', function(d) {
   //   
   //       })
    }
}
//initboard()



initboard();