$(document).ready(function() {
    update_bestiary_form_with_query();
    update_inventory();
    initialize_table();
    initialize_charts();
})

function update_bestiary_form_with_query(){
    var params = new URLSearchParams(location.search)

    update_form_text_from_query(params, 'name');

    update_form_multislider_from_query(params, 'natural_stars');
    update_form_multislider_from_query(params, 'skills__cooltime');
    update_form_multislider_from_query(params, 'skills__hits');

    update_form_multiselect_from_query(params, 'awaken_level');
    update_form_multiselect_from_query(params, 'element');
    update_form_multiselect_from_query(params, 'archetype');
    update_form_multiselect_from_query(params, 'buffs');
    update_form_multiselect_from_query(params, 'debuffs');
    update_form_multiselect_from_query(params, 'other_effects');
    update_form_multiselect_from_query(params, 'skills__scaling_stats__pk');
    update_form_multiselect_from_query(params, 'leader_skill__attribute');
    update_form_multiselect_from_query(params, 'leader_skill__area');

    update_form_select_from_query(params, 'skills__passive');
    update_form_select_from_query(params, 'skills__aoe');
    update_form_select_from_query(params, 'fusion_food');

    update_form_toggle_from_query(params, 'effects_logic');
}

function clean_bestiary_url_data(data){
    var cleanedParams = clean_query_params(data)
    var params = new URLSearchParams(cleanedParams)
    var multiSliderParams = ['natural_stars', 'skills__cooltime', 'skills__hits']
    var newData = clean_multi_slider_min_max_params(params, multiSliderParams)
    return newData
}

function update_inventory() {
    $('#FilterBestiaryForm').submit();
}

function initialize_table() {
    var bestiary_table = $('#bestiary_table');
    bestiary_table.tablesorter({
        widgets: ['saveSort', 'columnSelector', 'stickyHeaders'],
        serverSideSorting: true,
        widgetOptions: {
            filter_reset: '.reset',
            columnSelector_container : '#column-selectors',
            columnSelector_saveColumns: true,
            columnSelector_mediaquery: false,
            columnSelector_layout: '<div class="form-check me-3"><label class="form-check-label"><input class="form-check-input" type="checkbox">{name}</label></div>',
            stickyHeaders_zIndex : 2,
            stickyHeaders_offset: 50
        },
        theme: 'bootstrap',
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
            chart_div.highcharts(data);
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
        var formData = clean_bestiary_url_data($form.serialize())
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: formData
        }).done(function (data) {
            history.replaceState({}, "", this.url.substring(0, this.url.indexOf('/inventory/')) + '/?' + formData)

            ToggleLoading($('body'), false);
            $('#bestiary-inventory').replaceWith(data);

            //Reinit everything
            initialize_table();
            $('[data-toggle="tooltip"]').tooltip({
                container: 'body'
            });
            $('[data-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });
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

        //Select2 inputs
        $form.find('select').each(function() {
            $(this).val(null).trigger("change");
        });

        //Sliders
        $form.find("[data-provide='slider']").each(function() {
            var $el = $(this),
                min = $el.data('slider-min'),
                max = $el.data('slider-max');
            $(this).slider('setValue', [min, max]);
        });

        // Toggle button
        $("input[name='effects_logic']").prop("checked", false);
        $("input[name='effects_logic']").parent().addClass('off');

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
    });