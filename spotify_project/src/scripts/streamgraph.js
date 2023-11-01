// Set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 300, left: 20},
    width = window.innerWidth - margin.left - margin.right,
    height = window.innerHeight - margin.top - margin.bottom;

// Append the svg object to the body of the page
var svg = d3.select("#streamgraph").append("svg")
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

    // Group the data by hour intervals and calculate the sum of time for each prodctivity group
    var groupedData = d3.nest()
        .key(function(d) {
            var date = new Date(d.date); // Convert the time string to a Date object
            var hours = date.getHours();
            return hours; // Return the time in "HH:MM" format
        })
        .key(function(d) { return d.productivity; })
        .rollup(function(v) { return d3.sum(v, function(d) { return d.time; }); })
        .entries(data);

    var keys = ["-2", "-1", "0", "1", "2"];
    var stack = d3.stack()
        .keys(keys);

    // Transform the data
    var transformedData = groupedData.map(function(d) {
        var obj = {hour: parseInt(d.key, 10)};
        keys.forEach(function(key) {
            var found = d.values.find(function(v) { return v.key === key; });
            obj[key] = found ? found.value : 0;
        });
        return obj;
    });

    // Sort the ratio array by key
    transformedData.sort(function(a, b) {
        return d3.descending(a.hour, b.hour);
    });

    // // Calculate the maximum sum of productivities per hour
    // var maxSum = d3.max(transformedData, function(d) {
    //     return keys.reduce(function(acc, key) {
    //         return acc + d[key];
    //     }, 0);
    // });

    // maxSum = maxSum/3600;

    place_hours(svg, 20, height+40, width);

    var x = d3.scaleLinear()
        .domain(d3.extent(transformedData, function(d) { return d.hour; }))
        .range([0, width]);

    var y = d3.scaleLinear()
        .domain([0, d3.max(transformedData, function(d) { return d["-2"] + d["-1"] + d["0"] + d["1"] + d["2"]; })])
        .range([height, 0]);

    var color = d3.scaleOrdinal(d3.schemeCategory10);

    var stack = d3.stack()
        .keys(["2", "1", "0", "-1", "-2"])
        .offset(d3.stackOffsetWiggle);

    var series = stack(transformedData);

    var area = d3.area()
        .x(function(d, i) { return x(d.data.hour); })
        .y0(function(d) { return y(d[0]); })
        .y1(function(d) { return y(d[1]); });

    // create a tooltip
    var Tooltip = svg
        .append('text')
        .attr('x', 100)
        .attr('y', 0)
        .style('opacity', 0)
        .style('fill', 'green')
        .style('font-size', 17);

    // Three function that change the tooltip when user hover / move / leave a cell
    var mouseover = function(d) {
        Tooltip.style('opacity', 1)
        d3.selectAll('.area').style('opacity', 0.8)
        d3.select(this)
            .style('stroke', 'black')
            .style('opacity', 1)
            .style('fill', 'red')
    };

    var mousemove = function(d, i) {
        mouse_pos = d3.mouse(this)
        x_pos = Math.round(mouse_pos[0] / (width / d.length))
        // y_val = Math.abs(d[x_pos][1] - d[x_pos][0])
        grp = keys[i]

        // //retrieving the month
        // month = x_pos % 12
        // year = Math.floor(x_pos / 12)

        // //retrieving the year
        // month_str = months_dict[month]
        // year_str = year + 2001

        // //setting the text in the tooltip
        // str = y_val.toString() + ' ' + grp.toString() + ' recorded during the month ' + month_str + ' ' + year_str
        Tooltip.text(grp)
    };

    var mouseleave = function(d, i) {
        Tooltip.style('opacity', 0)
        d3.selectAll('.area')
            .style('opacity', 0.8)
            .style('stroke', 'none')
            .style('fill', function(d, i) {
                return color(i)
            })
    };

    svg.selectAll(".area")
        .data(series)
        .enter().append("path")
        .attr("class", "area")
        .attr("d", area)
        .style("fill", function(d, i) { return color(i); })
        .style('opacity', 0.8)
        .on('mouseover', mouseover)
        .on('mousemove', mousemove)
        .on('mouseleave', mouseleave);

});

function place_hours(svg, x, y, max_width) {
    var step_size = max_width / 24
    for (var i = 0; i < 24; i++) {
      var hour = i

      svg.append('text')
        .attr('text-anchor', 'end')
        .attr('x', x + step_size * i)
        .attr('y', y)
        .style('fill', 'black')
        .text(hour.toString())
    }
};
