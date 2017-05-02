var dialog;

$(document).ready(function() {
    UpdateCharts();
});

function UpdateCharts(in_tab_only) {
    var $charts;
    if (in_tab_only) {
        $charts = $('.tab-pane.active .chart')
    }
    else {
        $charts = $('.chart').not('.tab-pane .chart').add('.tab-pane.active .chart')
    }
    $charts.each(function() {
        $.ajax({
            url: $(this).data('chart-data-source'),
            type: 'get',
            global: false,
            context: this,
            cache: false
        }).done(function(result) {
            $(this).highcharts(result);
        });
    });
}

$('body')
    .on('submit', '.ajax-form', function() {
        //Handle add ajax form submit
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function(response) {
            if (response.success == true) {
                location.reload();
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.log-menu .dropdown-toggle', function() {
        // Close other dropdowns and open this one
        $('.dropdown-toggle').parent().toggleClass('open', false);
        $(this).parent().toggleClass('open');
    })
    .on('click', '.set-timespan', function() {
        var span = $(this).data('timespan');
        if (span) {
            $.ajax({
                type: 'get',
                url: '/data/log/timespan/' + span + '/',
                global: false
            }).done(function (response) {
                if (response.success == true) {
                    location.reload();
                }
            });
        }
    })
    .on('shown.bs.tab', function() {
        UpdateCharts(true);
    });