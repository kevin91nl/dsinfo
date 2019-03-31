function render_papers() {
    d3.json('/static/data/papers.json', function (d) {
        var papers = d['papers'];

        d3.select('#papers table').remove();

        var table = d3.select('#papers').append('table').attr('class', 'table table-hover table-dark');
        var thead = table.append('thead');
        var tbody = table.append('tbody');

        var headers = {
            'Date': 'date',
            'Categories': 'category',
            'Title': 'title'
        };

        thead.append('tr')
            .selectAll('th')
            .data(d3.keys(headers)).enter()
            .append('th')
            .text(function (column) {
                return column;
            })
        ;

        var rows = tbody.selectAll('tr')
            .data(papers)
            .enter()
            .append('tr')
        ;

        rows.selectAll('td')
            .data(function (row) {
                result = [];
                for (column of d3.values(headers)) {
                    var subresult = {
                        'column': column,
                        'value': row[column],
                        'link': false,
                        'title': ''
                    };
                    if (column == 'title') {
                        subresult['link'] = row['link'];
                        subresult['title'] = row['comment'];
                    }
                    result.push(subresult);
                }
                return result
            })
            .enter()
            .append('td')
            .html(function (d) {
                if (d.link !== false) {
                    return '<a href="' + d.link + '" target="_blank" title="' + d.title + '">' + d.value + '</a>';
                } else {
                    return d.value;
                }
            })

        // var cells = rows.selectAll('tr')
        //     .data(function (row) {
        //         return row;
        //     })
        //     .enter()
        //     .append('td')
        //     .append('a')
        //     .attr('target', '_blank')
        //     .attr('title', function(d) {
        //         return d.title
        //     })
        //     .attr('href', function (d) {
        //         return d.link;
        //     })
        //     .text(function (d) {
        //         return d.value;
        //     })

        // table.append('tbody').append('tr')
        //     .selectAll('td')
        //         .data(function (row) {
        //             return {'a': 'b'}
        //         })
        //     .enter()
        //     .append('td')
        //     .text(function (d) { return d.value; })

    });
}

render_papers();
setInterval(render_papers, 60000);