$(document).ready(function() {
    update_inventory();
    initialize_charts();
});

function update_inventory() {
    $('#FilterBestiaryForm').submit();
}

function initialize_charts() {
    $('.bestiary-stat-chart').each( function() {
        var monster_id = $(this).data('monster');
        var chart_div = $(this);
        $.ajax({
            dataType: "json",
            url: API_URL + 'bestiary/' + monster_id.toString() + '/chart/',
            global: false
        }).done(function(data) {
            chart_div.highcharts({
                chart: {
                    type: 'line'
                },
                title: {
                    text: 'Stat Growth By Level'
                },
                xAxis: {
                    tickInterval: 5,
                    showFirstLabel: true
                },
                yAxis: [
                    {
                        title: {
                            text: 'HP'
                        },
                        id: 'hp',
                        opposite: true
                    },
                    {
                        title: {
                            text: 'ATK DEF'
                        },
                        id: 'atkdef'
                    }
                ],
                series: data
            });
        })
    });
}

function AddMonster(monster_pk, stars) {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/add/?monster=' + monster_pk.toString() + '&stars=' + stars.toString(),
        type: 'get'
    }).done( function(result) {
        bootbox.dialog({
            title: "Add Monster",
            message: result.html
        });
        $('.rating').rating();
    })
}


$('body')
    .on('click', '.monster-add', function() { AddMonster($(this).data('monster'), $(this).data('stars')) })
    .on('submit', '#FilterBestiaryForm', function() {
        ToggleLoading($('body'), true);

        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            ToggleLoading($('body'), false);
            $('#bestiary-inventory').replaceWith(data);

            //Reinit everything
            $('[data-toggle="tooltip"]').tooltip({
                container: 'body'
            });
            $('[data-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });
            var bestiary_table = $('#bestiary_table');
            bestiary_table.tablesorter({
                widgets: ['saveSort', 'columnSelector', 'stickyHeaders'],
                serverSideSorting: true,
                widgetOptions: {
                    filter_reset: '.reset',
                    columnSelector_container : '#column-selectors',
                    columnSelector_saveColumns: true,
                    columnSelector_mediaquery: false,
                    columnSelector_layout: '<label class="checkbox-inline"><input type="checkbox">{name}</label>',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 50
                }
            })
            .bind('sortBegin', function(e, table) {
                var sortColumn = e.target.config.sortList[0][0];
                var sortDirection = e.target.config.sortList[0][1] == 0 ? 'desc' : 'asc';
                var column_name = $(table).find('th')[sortColumn].textContent;
                var sort_header = slugify(column_name);

                $('#id_sort').val(sort_header + ';' + sortDirection);
                update_inventory();
            });

            // Trigger a sort reset if the sort form field is empty
            if (!$('#id_sort').val()) {
                bestiary_table.trigger('sortReset');
                bestiary_table.trigger('saveSortReset');
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.reset', function() {
        $('#monster_table').trigger('sortReset');
        var $form = $('#FilterBestiaryForm');
        $form[0].reset();
        $form.find('select').each(function() {
            $(this).val(null).trigger("change");
        });
        $('#id_sort').val('');

        update_inventory();
    })
    .on('click', '.pager-btn', function() {
        $('#id_page').val($(this).data('page'));
        update_inventory();
    })
    .on('shown.bs.collapse', '#monsterFilterCollapse', function() {
        $("[data-provide='slider']").slider('relayout');
    })
    .on('submit', '.ajax-form', function() {
        //Handle add ajax form submit
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function(data) {
            if (data.code === 'success') {
                $('.modal.in').modal('hide');
            }
            else {
                $form.replaceWith(data.html);
                $('.rating').rating();
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.edit-skill', function() {
        var skill_id = $(this).data('skill-id');

        $.ajax({
            type: 'get',
            url: '/bestiary/edit/skill/' + skill_id + '/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Edit Skill",
                size: "large",
                message: data.html
            });
        });
    });
