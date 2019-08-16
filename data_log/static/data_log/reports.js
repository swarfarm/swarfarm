$('document').ready(initialize_charts);

function initialize_charts() {
    $('.report-chart').each( function() {
        var chart_div = $(this);
        var data = chart_div.data('chart');
        console.log(data);
        chart_div.highcharts(data);
    });
}
