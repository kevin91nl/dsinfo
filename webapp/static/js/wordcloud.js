// function create_wordcloud(selector) {
//     var margin = {top: 30, right: 50, bottom: 30, left: 50};
//     var width = parseInt(selector.style('width').slice(0, -2)) - margin.left - margin.right;
//     var height = parseInt(selector.style('height').slice(0, -2)) - margin.top - margin.bottom;
//
//     var g = selector
//         .append("g")
//         .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
//
//     function process_wordcloud_data(words) {
//         var data = words['stats'];
//         var color = d3.scaleOrdinal(d3.schemeSpectral[9]);
//         var fontSize = d3.scaleLinear().domain([0, 200]).range([0, width / 50]);
//
//         d3.layout.cloud()
//             .size([width, height])
//             .padding(5)
//             .timeInterval(20)
//             .words(data)
//             .rotate(function (d) {
//                 return 0;
//             })
//             .fontSize(function (d, i) {
//                 return fontSize(d.tfidf);
//             })
//             //.fontStyle(function(d,i) { return fontSyle(Math.random()); })
//             .fontWeight(["bold"])
//             .text(function (d) {
//                 return d.word;
//             })
//             .spiral("archimedean") // "archimedean" or "rectangular"
//             .on("end", draw)
//             .start();
//
//         var wordcloud = g.append("g")
//             .attr('class', 'wordcloud')
//             .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
//
//         g.append("g")
//             .attr("class", "axis")
//             .attr("transform", "translate(0," + height + ")")
//             .selectAll('text')
//             .style('font-size', '20px')
//             .style('fill', function (d) {
//                 return color(d);
//             })
//             .style('font', 'Impact');
//
//         function draw(words) {
//             wordcloud.selectAll("text")
//                 .data(words)
//                 .enter().append("text")
//                 .attr('class', 'word')
//                 .style("fill", function (d, i) {
//                     return color(i);
//                 })
//                 .style("font-size", function (d) {
//                     return d.size + "px";
//                 })
//                 .style("font-family", function (d) {
//                     return 'Impact';
//                 })
//                 .attr("text-anchor", "middle")
//                 .attr("transform", function (d) {
//                     return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
//                 })
//                 .text(function (d) {
//                     return d.text;
//                 });
//         }
//
//     }
//
//     function render() {
//         d3.json('/static/data/words.json').then(process_wordcloud_data);
//     }
//
//     window.addEventListener("resize", render);
//
//     render();
//     setInterval(render, 10000);
// }
//
// create_wordcloud(d3.select("#wordcloud"));

function wordCloud(selector) {

    var fill = d3.scale.category20();


    //Construct the word cloud's SVG element
    var svg = d3.select(selector).append("svg")
        .attr("width", 250)
        .attr("height", 250)
        .append("g")
        .attr("transform", "translate(125,125)")
    ;


    //Draw the word cloud
    function draw(words) {
        var cloud = svg.selectAll("g text")
                        .data(words, function(d) { return d.text; });

        //Entering words
        cloud.enter()
            .append("text")
            .style("font-family", "Impact")
            .style("fill", function(d, i) { return fill(i); })
            .attr("text-anchor", "middle")
            .attr('font-size', 1)
            .text(function(d) { return d.text; });

        //Entering and existing words
        cloud
            .transition()
                .duration(600)
                .style("font-size", function(d) { return d.size + "px"; })
                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .style("fill-opacity", 1);

        //Exiting words
        cloud.exit()
            .transition()
                .duration(200)
                .style('fill-opacity', 1e-6)
                .attr('font-size', 1)
                .remove();
    }


    //Use the module pattern to encapsulate the visualisation code. We'll
    // expose only the parts that need to be public.
    return {

        //Recompute the word cloud for a new set of words. This method will
        // asycnhronously call draw when the layout has been computed.
        //The outside world will need to call this function, so make it part
        // of the wordCloud return value.
        update: function(words) {
            console.log(words);
            d3.layout.cloud().size([250, 250])
                .words(words)
                .padding(5)
                .rotate(function() { return ~~(Math.random() * 2) * 90; })
                .font("Impact")
                .fontSize(function(d) { return d.size; })
                .on("end", draw)
                .start();
        }
    }

}

//Create a new instance of the word cloud visualisation.
var wordCloud = wordCloud('#wordcloud');

//Start cycling through the demo data
//showNewWords(myWordCloud);

function update() {
    d3.json('/static/data/words.json?nocache=' + (new Date).getTime(), function (data) {
        words = data['stats'];
        words = words.map(function (d) {
            return {
                text: d.word,
                size: d.tfidf / 10
            }
        });
        wordCloud.update(words);
    });
}
update();
setInterval(update, 60000);