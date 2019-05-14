var margin = {
  top: 20,
  right: 10,
  bottom: 20,
  left: 10
};
var width = 980 - margin.left - margin.right;
var height = 510 - margin.top - margin.bottom;
var padding = 20;

var ind = "ks"
buttonUpdate()

function buttonUpdate(){
  var kospi_btn = document.getElementById("kospi-btn");
  var kosdaq_btn = document.getElementById("kosdaq-btn");
  if (ind =="ks"){
    kospi_btn.classList.add("kospi-btn");
    kosdaq_btn.classList.remove("kosdaq-btn");
  }else{
    kospi_btn.classList.remove("kospi-btn");
    kosdaq_btn.classList.add("kosdaq-btn");
  }
}

function circleColor(){
  if (ind =="ks"){
    color="#0085CA";
  }else{
    color="#CA0043";
  }
  return color
}

function select(category) {
  ind = category;
  buttonUpdate();
  updateData(ind);
}

function formatMarketCap(num) {
    billions = num/1.0e+12;
   if (billions>1){
     rounded = billions.toFixed(2) + "B";
   }else{
     rounded = (num/1.0e+9).toFixed(2) + "M";
   }
   return rounded;
}

var svg = d3.select("#chart-area")
  .append("svg")
  //.attr("width", width)
  //.attr("height", height)
  //responsive SVG needs these 2 attributes and no width and height attr
  .attr("preserveAspectRatio", "xMinYMin meet")
  .attr("viewBox", "0 0 "+width+" "+height+"")

var g = svg.append("g")
  .attr("transform", "translate(0,-30)");

//xAxis label
g.append("text")
  .attr("text-anchor","middle")
  .attr("x", width/2)
  .attr("y", height + margin.bottom)
  .attr("class", "x-label")
  .text("Share price change(%)")

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

// g.selectAll(".tick").selectAll('line')
//   .attr("class","dash-stroke")
//   .attr("stroke", "#777").attr("stroke-dasharray", "2,2");
//
// g.selectAll(".tick:not(:first-of-type)").selectAll('line')
//   .attr("stroke", "#777").attr("stroke-dasharray", "2,2");

//initial page loading
updateData(ind);


function updateData(ind) {
  d3.csv("https://raw.githubusercontent.com/summerohoh/FTgraphics/master/test/test1.csv")
    .then(function(data) {
      var nodes = data.map(function(node, index) {
        return {
          index: index,
          exchange: node["Exchange"],
          code: node["Code"],
          name:node["Issue Name"],
          marketcap: parseFloat(node["Market Cap(KRW)"].replace(/,/g, '')),
          formattedMarketCap:formatMarketCap(parseFloat(node["Market Cap(KRW)"].replace(/,/g, ''))),
          capweight: +node["Index Market Cap weight(%)"],
          changes: +node["Share Price Change(%)"],
          initprice: +node["Price on 20171228"],
          finalprice: +node["Price on 20181228"],
          fx: x(parseFloat(node["Share Price Change(%)"].replace(/,/g, '')))
        };
      });

      console.log(nodes);

      var circleSize = d3.scaleSqrt()
        .domain([0, d3.max(nodes, function(d) {
          return d.marketcap
        })])
        .range([0, 50]);

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
        .attr("class","dash-stroke")


        var formatLegend = function(d) {
            return Math.round(d/1.0e+12) + "B";
          }


        var circleKey = circleLegend()
            .scale(circleSize)
            .tickValues([1000000000000,10000000000000,50000000000000, 100000000000000])
            .tickFormat(formatLegend)
            .tickPadding(5)
            .tickExtend(20)
            .orient("right") //default

        svg.append('g')
          .attr('transform', 'translate(850, 100)')
          .call(circleKey)

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
          .style("fill", circleColor())

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
                "<div class='info-box'><p>"+
                "<span class='description'>" +d.name +"</span><br>" +
                "<span class='code'>"+d.code+"."+d.exchange+"</span>  | " +
                "<span class=''>Market Cap: "+d.formattedMarketCap+"<span>" +
                "</p></div>"
              )
                .style("visibility", "visible");
          })
	        .on("mousemove", function(){return tooltip.style("top", (event.pageY-40)+"px").style("left",(event.pageX+20)+"px");})
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

      //legend
      // var scale = d3.scaleSqrt()
      //             .domain([0, 1000000])
      //             .range([0, 100])
      //
      // scale.domain([0,1000000])


    }).catch(function(error) {
      console.log(error);
    })
}
