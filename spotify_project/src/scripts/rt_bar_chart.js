// Set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 20, left: 40},
    width = window.innerWidth/4 - margin.left - margin.right,
    height = window.innerHeight/3 - margin.top - margin.bottom;

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
    var select_device = d3.select("#RT").append("select")
        .attr("id", "deviceSelect")
        .style("position", "absolute");
    select_device.selectAll("option")
        .data(devices)
        .enter().append("option")
        .text(function(d) { return d; });

    // Populate the select element with options
    var select_productivity = d3.select("#RT").append("select")
        .attr("id", "productivitySelect")
        .style("position", "absolute")
        .style("top", "20px")
        // .style("top", "10px")
        // .style("right", "10px");
    select_productivity.selectAll("option")
        .data(productivities)
        .enter().append("option")
        .text(function(d) { return d; })

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
        d3.select("#productivityhourlysubgraph").remove();
        d3.select("#devicesubgraph").remove();
        d3.select("#productivitysubgraph").remove();

        updateSubgraphs(data, d)
    });

    // Add the event listener to the body
    d3.select('#RT').on('click', function() {
        // Check if the event target is part of the bar plot
        if (!d3.select(d3.event.target).classed('bar')) {
        // If not, reset the subplots
        d3.select("#activitysubgraph").remove();
        d3.select("#categorysubgraph").remove();
        d3.select("#productivityhourlysubgraph").remove();
        d3.select("#devicesubgraph").remove();
        d3.select("#productivitysubgraph").remove();

        updateSubgraphs(data);
    }
  });
};

function updateSubgraphs(data, d = null){
    //TODO: maybe add class inheritance here:
    updateActivitySubgraph(data, d);
    updateCategorySubgraph(data, d);
    updateProductivityHourlySubgraph(data, d);
    updateDeviceSubgraph(data, d);
    updateProductivitySubgraph(data, d)
};

function updateProductivitySubgraph(data, d = null){
    // Create a new SVG for the subgraph
    var subgraphSvg = d3.select("body").append("svg")
    .attr("id", "productivitysubgraph")
    .attr("width", 2*width + margin.left + margin.right)
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
    // Group the data by hour intervals and calculate the sum of time for each prodctivity group
    var groupedData = d3.nest()
        .key(function(d) {
            var date = new Date(d.date); // Convert the time string to a Date object
            var hours = date.getHours();
            return hours; // Return the time in "HH:MM" format
        })
        .key(function(d) { return d.productivity; })
        .rollup(function(v) { return d3.sum(v, function(d) { return d.time; }); })
        .entries(subgraphData);

    // Sort the ratio array by key
    groupedData.sort(function(a, b) {
        return d3.ascending(a.key, b.key);
    });

    var keys = ["2", "1", "0", "-1", "-2"];
    var stack = d3.stack()
        .keys(keys);

    // Transform the data
    var transformedData = groupedData.map(function(d) {
        var obj = {hour: d.key};
        keys.forEach(function(key) {
            var found = d.values.find(function(v) { return v.key === key; });
            obj[key] = found ? found.value : 0;
        });
        return obj;
    });

    // Calculate the maximum sum of productivities per hour
    var maxSum = d3.max(transformedData, function(d) {
        return keys.reduce(function(acc, key) {
            return acc + d[key];
        }, 0);
    });

    maxSum = maxSum/3600;

    // Create the y-scale
    var y = d3.scaleLinear()
        .domain([0, maxSum])
        .range([height, 0]);

    // Create the x-scale
    var x = d3.scaleBand()
        .range([0, 2*width])
        .padding(0.1);

    // Sort the transformed data by hour
    transformedData.sort(function(a, b) {
        return d3.ascending(parseInt(a.hour), parseInt(b.hour));
    });

    // Set the domain of the x-scale
    x.domain(transformedData.map(function(d) { return d.hour; }));

    // Generate the stack data
    var stackData = stack(transformedData)

    // Create the color scale
    var color = d3.scaleOrdinal()
        .domain(keys)
        .range(["green", "yellow", "black", "orange", "red"]);

    // Create the bars
    var bars = subgraphSvg.selectAll("g")
        .data(stackData)
        .enter().append("g")
        .style("fill", function(d) { return color(d.key); });

    // Create the segments
    bars.selectAll("rect")
        .data(function(d) { return d; })
        .enter().append("rect")
        .attr("x", function(d) { return x(d.data.hour); })
        .attr("y", function(d) { return y(d[1]/3600); })
        .attr("height", function(d) { return y(d[0]/3600) - y(d[1]/3600); })
        .attr("width", x.bandwidth());

    // Create the x-axis generator
    var xAxis = d3.axisBottom(x);

    // Append the x-axis
    subgraphSvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Create the y-axis generator
    var yAxis = d3.axisLeft(y);

    // Append the y-axis
    subgraphSvg.append("g")
        .call(yAxis);
}

function updateDeviceSubgraph(data, d = null){
    // Create a new SVG for the subgraph
    var subgraphSvg = d3.select("body").append("svg")
    .attr("id", "devicesubgraph")
    .attr("width", 2*width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    if (!d){
        var subgraphData = data
        var ratio_n = 7
    }
    else {
        // Filter the data for the clicked bar
        var ratio_n = 1
        var subgraphData = data.filter(function(dataPoint) {
            return dataPoint.dayOfWeek == d.key;
        });
    }

    // Group the data by 10-minute intervals and calculate the sum of time for each group
    var groupedData = d3.nest()
        .key(function(d) {
            var date = new Date(d.date); // Convert the time string to a Date object
            var hours = date.getHours();
            var minutes = Math.floor(date.getMinutes() / 10) * 10; // Round down to the nearest 10
            return hours + ":" + (minutes < 10 ? "0" : "") + minutes; // Return the time in "HH:MM" format
        })
        .key(function(d) { return d.device; })
        .rollup(function(v) { return d3.sum(v, function(d) { return (100/ratio_n)*(d.time/(10*60)); }); })
        .entries(subgraphData);

    // Sort the ratio array by key
    groupedData.sort(function(a, b) {
        return d3.ascending(a.key, b.key);
    });

    // Create an array with all possible 10-minute intervals
    var allIntervals = [];
    for (var i = 0; i < 24; i++) {
        for (var j = 0; j < 60; j += 10) {
        var key = i + ":" + (j < 10 ? "0" : "") + j;
        allIntervals.push({ key: key, ratio: 0 });
        }
    }

    // Merge the allIntervals array with the ratio array
    var ratio = allIntervals.map(function(d) {
        var found = groupedData.find(function(r) { return r.key === d.key; });
        if (found) {
            var mobileData = found.values.find(function(v) { return v.key === 'mobile'; });
            var computerData = found.values.find(function(v) { return v.key === 'computers'; });
            return {
                key: d.key,
                values: [
                    { key: 'mobile', value: mobileData ? mobileData.value : 0 },
                    { key: 'computers', value: computerData ? computerData.value : 0 }
                ]
            };
        } else {
            return {
                key: d.key,
                values: [
                    { key: 'mobile', value: 0 },
                    { key: 'computers', value: 0 }
                ]
            };
        }
    });

    console.log(ratio)

    // Create the x scale
    var x = d3.scaleLinear()
        .domain([0, 24])
        .range([0, 2*width]);

    // Flatten the values arrays and find the maximum value
    var maxValue = d3.max(ratio, function(d) {
        return d3.max(d.values, function(v) {
            return v.value;
        });
    });
    // Create the y scale
    var y = d3.scaleLinear()
        .domain([0, maxValue])
        .range([height, 0]);

    // Create the line generator
    var line_computer = d3.line()
        .x(function(d) {
            var timeParts = d.key.split(":");
            return x(+timeParts[0] + (+timeParts[1] / 60)); // Convert "HH:MM" to hours
        })
        .y(function(d) { return y(d.values.find(function(v) { return v.key === 'computers'; }).value); });

    var line_mobile = d3.line()
        .x(function(d) {
            var timeParts = d.key.split(":");
            return x(+timeParts[0] + (+timeParts[1] / 60)); // Convert "HH:MM" to hours
        })
        .y(function(d) { return y(d.values.find(function(v) { return v.key === 'mobile'; }).value); });

    // Add the line to the SVG
    subgraphSvg.append("path")
        .datum(ratio)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 1.5)
        .attr("d", line_mobile);

    // Add the line to the SVG
    subgraphSvg.append("path")
        .datum(ratio)
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 1.5)
        .attr("d", line_computer);

    // Add the x axis
    subgraphSvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).ticks(24).tickFormat(function(d) { return d; }));

    // Add the y axis
    subgraphSvg.append("g")
        .call(d3.axisLeft(y).ticks(5).tickFormat(function(d) { return d + " %"; }));

    // Add the title
    subgraphSvg.append("text")
        .attr("x", 150)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .text("Computer vs mobile use");
};

function updateProductivityHourlySubgraph(data, d = null){
    // Create a new SVG for the subgraph
    var subgraphSvg = d3.select("body").append("svg")
    .attr("id", "productivityhourlysubgraph")
    .attr("width", 2*width + margin.left + margin.right)
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

    // Group the data by 10-minute intervals and calculate the sum of time for each group
    var groupedData = d3.nest()
        .key(function(d) {
            var date = new Date(d.date); // Convert the time string to a Date object
            var hours = date.getHours();
            var minutes = Math.floor(date.getMinutes() / 10) * 10; // Round down to the nearest 10
            return hours + ":" + (minutes < 10 ? "0" : "") + minutes; // Return the time in "HH:MM" format
        })
        .key(function(d) { return d.productivity; })
        .rollup(function(v) { return d3.sum(v, function(d) { return d.time; }); })
        .entries(subgraphData);

    groupedData.forEach(function(d) {
        d.ratio = d.values.reduce(function(sum, p) { return sum + p.value * p.key; }, 0);
    });

    var ratio = d3.nest()
        .key(function(d) { return d.key; })
        .rollup(function(v) { return d3.sum(v, function(d) { return d.ratio; }); })
        .entries(groupedData);

    ratio.forEach(function(d) {
        d.ratio = d.value / (2 * 3600) * 100;
    });

    // Create the x scale
    var x = d3.scaleLinear()
        .domain([0, 24])
        .range([0, 2*width]);

    // Create the y scale
    var y = d3.scaleLinear()
        .domain([d3.min(ratio, function(d) { return d.ratio; }), d3.max(ratio, function(d) { return d.ratio; })])
        .range([height, 0]);

    // Sort the ratio array by key
    ratio.sort(function(a, b) {
        return d3.ascending(a.key, b.key);
    });

    // Create an array with all possible 10-minute intervals
    var allIntervals = [];
    for (var i = 0; i < 24; i++) {
        for (var j = 0; j < 60; j += 10) {
        var key = i + ":" + (j < 10 ? "0" : "") + j;
        allIntervals.push({ key: key, ratio: 0 });
        }
    }

    // Merge the allIntervals array with the ratio array
    ratio = allIntervals.map(function(d) {
        var found = ratio.find(function(r) { return r.key === d.key; });
        return found ? found : d;
    });

    // Create the line generator
    var line = d3.line()
        .x(function(d) {
            var timeParts = d.key.split(":");
            return x(+timeParts[0] + (+timeParts[1] / 60)); // Convert "HH:MM" to hours
        })
        .y(function(d) { return y(d.ratio); });

    // Add the line to the SVG
    subgraphSvg.append("path")
        .datum(ratio)
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 1.5)
        .attr("d", line);

    // // Add the area under the line
    // subgraphSvg.append("path")
    //     .datum(ratio)
    //     .attr("fill", "green")
    //     .attr("fill-opacity", 0.3)
    //     .attr("d", d3.area()
    //     .x(function(d) { return x(d.key); })
    //     .y0(y(0))
    //     .y1(function(d) { return y(d.ratio); }));

    // Add the x axis
    subgraphSvg.append("g")
        .attr("transform", "translate(0," + 150 + ")")
        .call(d3.axisBottom(x).ticks(24).tickFormat(function(d) { return d; }));

    // Add the y axis
    subgraphSvg.append("g")
        .call(d3.axisLeft(y).ticks(5).tickFormat(function(d) { return d + " %"; }));

    // Add the title
    subgraphSvg.append("text")
        .attr("x", 150)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .text("Ratio of productivity");
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
