var updateInterval;
var dialog;
var importCancelled;

$(document).ready(function() {
    UpdateCharts();
});

function updateImportProgress() {
    $.ajax({
        type: 'get',
        url: '/data/import/progress/data/',
        global: false
    }).done(function(response) {
        var stage = response.stage;
        var current_progress = Math.floor((response.current / response.total) * 100);
        var parse_progress = 0;
        var monster_progress = 0;
        var rune_progress = 0;
        var craft_progress = 0;
        var $parse_bar = $('#progress-parse');
        var $monster_bar = $('#progress-monsters');
        var $rune_bar = $('#progress-runes');
        var $crafts_bar = $('#progress-crafts');

        switch(stage) {
            case "parse":
                break;
            case "monsters":
                parse_progress = 100;
                monster_progress = current_progress;
                break;
            case "runes":
                parse_progress = 100;
                monster_progress = 100;
                rune_progress = current_progress;
                break;
            case "crafts":
                parse_progress = 100;
                monster_progress = 100;
                rune_progress = 100;
                craft_progress = current_progress;
                break;
            case "done":
                parse_progress = 100;
                monster_progress = 100;
                rune_progress = 100;
                craft_progress = 100;
                clearTimeout(updateInterval);
                break;
        }

        // Set the progress and color for each bar
        if (parse_progress == 100) {
            $parse_bar.toggleClass('progress-bar-success', true);
            $parse_bar.toggleClass('active', false);
            $parse_bar.toggleClass('progress-bar-striped', false);
        }

        $monster_bar.css('width', monster_progress.toString() + '%');
        if (monster_progress == 100) {
            $monster_bar.toggleClass('progress-bar-success', true);
        }

        $rune_bar.css('width', rune_progress.toString() + '%');
        if (rune_progress == 100) {
            $rune_bar.toggleClass('progress-bar-success', true);
        }

        $crafts_bar.css('width', craft_progress.toString() + '%');
        if (craft_progress == 100) {
            $crafts_bar.toggleClass('progress-bar-success', true);
        }
    });
}

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
    .on('submit', '.import-form', function() {
        importCancelled = false;
        $('#submit-id-import').toggleClass('disabled', true);
        $.ajax({
            type: 'get',
            url: '/data/import/progress/'
        }).done(function (response) {
            dialog = bootbox.dialog({
                closeButton: false,
                onEscape: false,
                title: "Import Progress",
                message: response
            });
            updateInterval = setInterval(updateImportProgress, 2000)
        });
    })
    .on('submit', '.finalize-form', function() {
        $('#submit-id-finalize').prop('disabled', true);
        $('#submit-id-finalize').attr('value', 'Finalizing...');
    })
    .on('click', '.cancel-import', function() {
        importCancelled = true;
        window.stop();
        bootbox.hideAll();
        clearInterval(updateInterval);
        $('#submit-id-import').toggleClass('disabled', false);
    })
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