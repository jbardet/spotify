var margin = {top: 40, right: 150, bottom: 60, left: 30},
width = 2000,
height = 1000;

// append the svg object to the body of the page
var svg5 = d3.select("#my_dataviz")
.append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.append("g")
.attr("transform", "translate(" + 30 + "," + margin.top + ")");


// Load the data
// var dfd = require("danfojs-node")
let df = new dfd.readCSV("data/spotify.csv")

// Read the data
d3.csv("data/streamings.csv", function(data) {
    // scrollable menu to change graph
    var timeGroup = ['year', 'month', 'week', 'hour']
    var countGroup = ['count', 'time']

    //Create 1st scroll component
    var timeMenu = d3.select("#time_scroll")
    timeMenu.append("select")
    .selectAll('myOptions')
    .data(timeGroup)
    .enter()
    .append('option')
    .text(function (d) { return d; }) // text showed in the menu
    .attr("value", function (d) { return d; }) // corresponding value returned by the button


    //Create 2nd scroll component
    var countMenu = d3.select("#count_scroll")
    countMenu.append("select")
    .selectAll('myOptions')
    .data(countGroup)
    .enter()
    .append('option')
    .text(function (d) { return d; }) // text showed in the menu
    .attr("value", function (d) { return d; }) // corresponding value returned by the button

    // Not constant axis so will define later
    svg5
    .append("g")
    .attr("class",'axisBlack')
    .attr("transform", "translate(0," + height + ")")
    //.call(d3.axisBottom(x))
    .style("opacity", 1);

    // Add X axis label:
    var x_label = svg5.append("text")
    .attr("id", "x_label")
    .attr("text-anchor", "end")
    .attr("x", width-50)
    .attr("y", height+50 )
    .style("fill", "black")
    .text("Time")
    .attr("class", "bubble_legend");

    // Add Y axis
    const y = d3.scaleLinear()
    .domain([0, 240])
    .range([ height, 0])

    svg5
    .append("g")
    .attr("class",'axisBlack')
    .call(d3.axisLeft(y))
    .attr("transform", "translate(0,0)")
    .style("opacity", 1);

    // Add Y axis label:
    var y_label = svg5.append("text")
    .attr("id", "y_label")
    .attr("text-anchor", "end")
    .attr("x", 0)
    .attr("y", -20 )
    .style("fill", "black")
    .text("Count")
    .attr("class", "bubble_legend")
    .attr("text-anchor", "start")

    // Add a scale for bar size
    var z = d3.scaleSqrt()
    .domain([1, 300])
    .range([ 3, 15]);

    // A function that updates the bars
    function update(selectedTime, selectedCount) {
        // Create new data with the selection
        var dataFilterTime = data.filter(function(d){return d.time==parseInt(selectedTime)})
        // create an empty map and append
        var dataFilter = dataFilterTime.map(function(d){return {valueX: d[selectedX], valueY: d[selectedY],valueR: d[selectedR], type1 :d.type1, pokedex_number:d.pokedex_number , name:d.name, attack :d.attack , defense :d.defense, hp: d.hp, weight_kg:d.weight_kg, height_cm:d.height_cm, sp_attack: d.sp_attack, sp_defense: d.sp_defense, speed: d.speed}})

        let select = (value) => value;
        let group_df = df['ms_played'].groupby(df.ts.map(select(value)))
        if (selectedCount == "count") { return count }

        // let group_df = df['ms_played'].groupby(df["master_metadata_album_artist_name"]).sum()

        //update x-axis label
        var x_label_select = document.getElementById("time_scroll");
        var x_label = svg5.selectAll("#time_scroll")
        .text(x_label_select.options[x_label_select.selectedIndex].text);

        //update y-axis label
        var y_label_select = document.getElementById("count_scroll");
        var y_label = svg5.selectAll("#count_scroll")
        .text(y_label_select.options[y_label_select.selectedIndex].text);

        //update circles
        var u = d3.select("#graphArea").selectAll("#graphCircles")
        .data(dataFilter);

        // update bars
        // TO MODIFY
        u.enter()
        .append("circle").merge(u)
        .transition()
        .duration(1000)
        .attr("cx", function(d) { return x(+[d.valueX]) })
        .attr("cy", function(d) { return y(+[d.valueY]) })
        .attr("r", function (d) { return z(+[d.valueR]); } )
        .style("fill", function (d) { return (myColor(d.type1)); } )
        .attr("class", function(d) { return "bubbles " +d.type1 })
        .attr("id", "graphCircles")

        u.exit().remove();

        d3.select("#graphArea").selectAll("circle").on("mouseover", showTooltip);
        d3.select("#graphArea").selectAll("circle").on("mousemove", moveTooltip);
        d3.select("#graphArea").selectAll("circle").on("mouseleave", hideTooltip);
        x_label.exit().remove();
        y_label.exit().remove();
    }

    // When the button is changed, run the update function
    d3.select("#time_scroll").on("change", function(d) {
        // recover the option that has been chosen
        var selectedTime = document.getElementById('time_scroll').value
        var selectedCount = document.getElementById('count_scroll').value;
        // run the updateChart function with this selected option
        update(selectedTime, selectedCount)
    })

    // When the button is changed, run the update function
    d3.select("#count_scroll").on("change", function(d) {
        // recover the option that has been chosen
        var selectedTime = document.getElementById('time_scroll').value
        var selectedCount = document.getElementById('count_scroll').value;
        // run the updateChart function with this selected option
        update(selectedTime, selectedCount)
    })
})