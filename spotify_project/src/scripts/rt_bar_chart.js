// Set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 70, left: 40},
    width = 600 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

// Set the ranges
var x = d3.scaleBand().range([0, width]).padding(0.1);
var y = d3.scaleLinear().range([height, 0]);

// Append the svg object to the body of the page
var svg = d3.select("#RT").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// Load the data
d3.csv("data/rescuetime_activities.csv", function(error, data) {
    if (error) throw error;
    // Parse the date strings into Date objects and extract the day of the week
    var parseTime = d3.timeParse("%Y-%m-%d %H:%M:%S");
    data.forEach(function(d) {
    d.date = parseTime(d.date);
    if (d.date === null) {
        console.log("Invalid date string:", d);
    } else {
        d.dayOfWeek = d.date.getDay(); // 0 (Sunday) to 6 (Saturday)
    }
    });

    // Get the current date and time
    var now = new Date();

    // Filter out any dates that are more than 7 days old
    var oneWeekAgo = new Date();
    oneWeekAgo.setDate(now.getDate() - 7);
    data = data.filter(function(d) {
      return d.date >= oneWeekAgo;
    });

    // Get the unique values in the "device" column
    var devices = ["total", ...new Set(data.map(function(d) { return d.device; }))];
    // Get the unique values in the "productivity" column
    var productivities = ["all", ...new Set(data.map(function(d) { return d.productivity; }))];

    // Populate the select element with options
    var select_device = d3.select("#deviceSelect");
    select_device.selectAll("option")
        .data(devices)
        .enter().append("option")
        .text(function(d) { return d; });

    // Populate the select element with options
    var select_productivity = d3.select("#productivitySelect");
    select_productivity.selectAll("option")
        .data(productivities)
        .enter().append("option")
        .text(function(d) { return d; });

    // Add the x Axis
    var xAxisGroup = svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));
        // .attr("class", "x axis");

    // Add the y Axis
    var yAxisGroup = svg.append("g")
        .call(d3.axisLeft(y));

    // Add an event listener to the select element
    select_device.on("change", function() {
        // Get the selected device
        var selectedDevice = select_device.node().value;
        // Get the selected productivity
        var selectedProductivity = select_productivity.node().value;

        // Filter the data by the selected device and productivity
        var filteredData = data.filter(function(d) {
            return (selectedDevice === "total" || d.device === selectedDevice) &&
                    (selectedProductivity === "all" || d.productivity === selectedProductivity);
        });

        // Update the plot with the filtered data
        updatePlot(filteredData, xAxisGroup, yAxisGroup);
    });

    // Add an event listener to the select element
    select_productivity.on("change", function() {
        // Get the selected device
        var selectedDevice = select_device.node().value;
        // Get the selected productivity
        var selectedProductivity = select_productivity.node().value;

        // Filter the data by the selected device and productivity
        var filteredData = data.filter(function(d) {
            return (selectedDevice === "total" || d.device === selectedDevice) &&
                    (selectedProductivity === "all" || d.productivity === selectedProductivity);
        });

        // Update the plot with the filtered data
        updatePlot(filteredData, xAxisGroup, yAxisGroup);
    });

    // Get the selected device (initially computers)
    var selectedDevice = select_device.node().value;
    var selectedProductivity = select_productivity.node().value;

    // Filter the data by the selected device and productivity
    var filteredData = data.filter(function(d) {
        return (selectedDevice === "total" || d.device === selectedDevice) &&
                (selectedProductivity === "all" || d.productivity === selectedProductivity);
    });

    // Initial plot with all data
    updatePlot(filteredData, xAxisGroup, yAxisGroup);
    updateSubgraphs(filteredData)
});

function updatePlot(data, xAxisGroup, yAxisGroup) {
    // Group the data by day of the week and calculate the sum of time for each group
    var groupedData = d3.nest()
        .key(function(d) { return d.dayOfWeek; })
        .rollup(function(v) { return d3.sum(v, function(d) { return d.time; }); })
        .entries(data);

    // Define an array of all days
    var numDays = ['1', '2', '3', '4', '5', '6', '0']
    var allDays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    // Create a new array that includes all days
    var completeData = numDays.map(function(day) {
        // Find the corresponding day in groupedData
        var foundDay = groupedData.find(function(d) { return d.key === day; });

        // If the day is found, return it. Otherwise, return a new object with the day and a value of 0
        return foundDay ? foundDay : {key: day, value: 0};
    });

    // Scale the range of the data in the domains
    x.domain(completeData.map(function(d) { return d.key; }));
    y.domain([0, d3.max(completeData, function(d) { return d.value/3600; })]);

    // Append the rectangles for the bar chart
    var bars = svg.selectAll(".bar")
        .data(completeData, function(d) { return d.key; }); // Use the day of the week as the key
    bars.exit().remove();
    bars = bars.enter().append("rect").merge(bars)
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.key); })
        .attr("width", x.bandwidth())
        .attr("y", function(d) { return y(d.value/3600); })
        .attr("height", function(d) { return height - y(d.value/3600); });

    // Update the x Axis
    xAxisGroup
    // .transition() // Add a transition to animate the changes
    // .duration(1000) // Set the duration of the transition
    .call(d3.axisBottom(x).tickFormat(function(d) {
        return allDays[d]; // Map the numbers to the weekday names
      }));

    // Update the y Axis
    yAxisGroup
    // .transition() // Add a transition to animate the changes
    // .duration(1000) // Set the duration of the transition
    .call(d3.axisLeft(y).tickFormat(function(d) {
        return d + " h"; // Append " h" to the tick labels
      }));

    bars.on("click", function(d) {
        // Remove any existing subgraph
        d3.select("#activitysubgraph").remove();
        d3.select("#categorysubgraph").remove();

        updateSubgraphs(data, d)
    });

    // Add the event listener to the body
    d3.select('body').on('click', function() {
        // Check if the event target is part of the bar plot
        if (!d3.select(d3.event.target).classed('bar')) {
        // If not, reset the subplots
        d3.select("#activitysubgraph").remove();
        d3.select("#categorysubgraph").remove();
        updateSubgraphs(data);
    }
  });
};

function updateSubgraphs(data, d = null){
    //TODO: maybe add class inheritance here:
    updateActivitySubgraph(data, d);
    updateCategorySubgraph(data, d);
};

function updateActivitySubgraph(data, d = null){
    // Create a new SVG for the subgraph
    var subgraphSvg = d3.select("body").append("svg")
    .attr("id", "activitysubgraph")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    if (!d){
        var subgraphData = data
    }
    else {
        // Filter the data for the clicked bar
        var subgraphData = data.filter(function(dataPoint) {
            return dataPoint.dayOfWeek == d.key;
        });
    }

    // Group the data by activity and calculate the sum of time for each group
    var groupedData = d3.nest()
    .key(function(d) { return d.activity; })
    .rollup(function(v) { return d3.sum(v, function(d) { return d.time/3600; }); })
    .entries(subgraphData);


    // Sort the data by the sum of time and take the top 10 activities
    groupedData.sort(function(a, b) { return b.value - a.value; });
    groupedData = groupedData.slice(0, 10);

    // Create the scales for the subgraph
    var x = d3.scaleBand().range([0, width]).padding(0.1);
    var y = d3.scaleLinear().range([height, 0]);

    // Set the domains for the scales
    x.domain(groupedData.map(function(d) { return d.key; }));
    y.domain([0, d3.max(groupedData, function(d) { return d.value; })]);

    // Create the axes for the subgraph
    var xAxis = d3.axisBottom(x);
    var yAxis = d3.axisLeft(y);

    // Append the axes to the subgraph
    subgraphSvg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
    subgraphSvg.append("g")
    .attr("class", "y axis")
    .call(yAxis);

    // Append the rectangles for the subgraph bar chart
    subgraphSvg.selectAll(".bar")
    .data(groupedData)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function(d) { return x(d.key); })
    .attr("width", x.bandwidth())
    .attr("y", function(d) { return y(d.value); })
    .attr("height", function(d) { return height - y(d.value); });
};

function updateCategorySubgraph(data, d = null){
    // Create a new SVG for the subgraph
    var subgraphSvg = d3.select("body").append("svg")
    .attr("id", "categorysubgraph")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    if (!d){
        var subgraphData = data
    }
    else {
        // Filter the data for the clicked bar
        var subgraphData = data.filter(function(dataPoint) {
            return dataPoint.dayOfWeek == d.key;
        });
    }

    // Group the data by category and calculate the sum of time for each group
    var groupedData = d3.nest()
    .key(function(d) { return d.category; })
    .rollup(function(v) { return d3.sum(v, function(d) { return d.time/3600; }); })
    .entries(subgraphData);


    // Sort the data by the sum of time and take the top 10 categories
    groupedData.sort(function(a, b) { return b.value - a.value; });
    groupedData = groupedData.slice(0, 10);

    // Create the scales for the subgraph
    var x = d3.scaleBand().range([0, width]).padding(0.1);
    var y = d3.scaleLinear().range([height, 0]);

    // Set the domains for the scales
    x.domain(groupedData.map(function(d) { return d.key; }));
    y.domain([0, d3.max(groupedData, function(d) { return d.value; })]);

    // Create the axes for the subgraph
    var xAxis = d3.axisBottom(x);
    var yAxis = d3.axisLeft(y);

    // Append the axes to the subgraph
    subgraphSvg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
    subgraphSvg.append("g")
    .attr("class", "y axis")
    .call(yAxis);

    // Append the rectangles for the subgraph bar chart
    subgraphSvg.selectAll(".bar")
    .data(groupedData)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function(d) { return x(d.key); })
    .attr("width", x.bandwidth())
    .attr("y", function(d) { return y(d.value); })
    .attr("height", function(d) { return height - y(d.value); });
};
