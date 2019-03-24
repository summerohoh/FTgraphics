var margin = {
  top: 20,
  right: 10,
  bottom: 20,
  left: 10
};
var width = 850 - margin.left - margin.right;
var height = 500 - margin.top - margin.bottom;
var padding = 20;

var ind = "ks"

function select(category) {
  ind = category;
  updateData()
}

var svg = d3.select("#chart-area")
  .append("svg")
  .attr("width", width)
  .attr("height", height)

var g = svg.append("g")
  .attr("transform", "translate(0,-30)");

//xAxis label
g.append("text")
  .attr("x", width / 2)
  .attr("y", height + margin.bottom)
  .attr("text-anchor", "middle")
  .attr("font-size", "20px")
  .text("Share price change(%)");

//X Scale
var x = d3.scaleLinear()
  .domain([-80, 120])
  .range([0 + padding, width - padding]); //add padding so the circle does not get cutoff

//tooltip area
var tooltip = d3.select("body")
	.append("div")
    .attr("class","info-tip")
  	.style("position", "absolute")
  	.style("z-index", "10")
  	.style("visibility", "hidden")

//initial page loading
updateData();

function updateData() {
  d3.csv("https://raw.githubusercontent.com/summerohoh/FTgraphics/master/test4.csv")
    .then(function(data) {
      var nodes = data.map(function(node, index) {
        return {
          index: index,
          exchange: node["Exchange"],
          code: node["Code"],
          name:node["Issue Name"],
          marketcap: parseFloat(node["Market Cap(KRW)"].replace(/,/g, '')),
          capweight: +node["Index Market Cap weight(%)"],
          changes: +node["Share Price Change(%)"],
          sector: "Technology",
          //x: x(parseFloat(node["Share Price Change(%)"].replace(/,/g,''))),
          fx: x(parseFloat(node["Share Price Change(%)"].replace(/,/g, '')))
        };
      });

      console.log(ind)

      var circleSize = d3.scaleSqrt()
        .domain([0, d3.max(nodes, function(d) {
          return d.marketcap
        })])
        .range([0, 30]);

      var color = d3.scaleOrdinal()
        .domain(nodes.map(function(d) {
          return d.sector
        }))
        .range(d3.schemeSet3);

      //add xAxis generator
      var xAxis = d3.axisBottom(x)
        .ticks(8)
        .tickSize(-height)
        .tickFormat(function(d) {
          return d + "%";
        });

      g.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0,450)")
        .call(xAxis)
        .select(".domain").remove();

      g.selectAll(".tick").selectAll('line')
        .attr("stroke", "#777").attr("stroke-dasharray", "2,2");

      g.selectAll(".tick:not(:first-of-type)").selectAll('line')
        .attr("stroke", "#777").attr("stroke-dasharray", "2,2");

      //Apply force layout to nodes
      var simulation = d3.forceSimulation(nodes)
        .force("y", d3.forceY(230))
        .force("charge", d3.forceManyBody().strength(-5))
        .force("x", d3.forceX().x(function(d) {
          return x(d.changes);
        }))
        //.force("center", d3.forceCenter(height/2,width/2))
        .force("collision", d3.forceCollide().radius(function(d) {
          return circleSize(d.marketcap)
        }))
        .on('tick', ticked);

      //Draw circles
      function ticked() {
        var u = g.selectAll('circle')
          //JOIN new data
          .data(nodes.filter(function(d) {
            return d.exchange == ind
          }))


        //EXIT old elements
        u.exit()
          .remove()

        //UPDATE old elements
        u
          .attr('r', function(d) {
            return circleSize(d.marketcap)
          })
          .attr('cx', function(d) {
            return d.x
          })
          .attr('cy', function(d) {
            return d.y
          })
          .style("stroke", "000")
          .style("fill", "0085CA")

        //ENTER
        u.enter()
          .append('circle')
          .attr('r', function(d) {
            return circleSize(d.marketcap)
          })
          .on("mouseover", function(d){
              d3.select(this)
                .transition()
                .attr('stroke-width',2)
              return tooltip.html(
                "<p>Code:"+d.code+"<br>" +
                "Name:"+d.name+"<br>" +
                "Marker Cap:"+d.marketcap+"<br>" +
                "</p>"
              )
                .style("visibility", "visible");
          })
	        .on("mousemove", function(){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
	        .on("mouseout", function(){
            d3.select(this)
              .transition()
              .attr('stroke-width',1)
            return tooltip.style("visibility", "hidden");})
          .attr('cx', function(d) {
            return d.x
          })
          .attr('cy', function(d) {
            return d.y
          })
          .style("stroke", "000")
          .style("fill", "0085CA")
          .style("opacity", 0.8)
      }
    }).catch(function(error) {
      console.log(error);
    })
}
