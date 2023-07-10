$(document).ready(function() {
    update_rune_builds_form_with_query();
    update_rune_builds_inventory();
});

function update_rune_builds_form_with_query(){
    var params = new URLSearchParams(location.search)
    
    update_form_multislider_from_query(params, 'avg_efficiency');
    update_form_multislider_from_query(params, 'hp');
    update_form_multislider_from_query(params, 'hp_pct');
    update_form_multislider_from_query(params, 'attack');
    update_form_multislider_from_query(params, 'attack_pct');
    update_form_multislider_from_query(params, 'defense');
    update_form_multislider_from_query(params, 'defense_pct');
    update_form_multislider_from_query(params, 'speed');
    update_form_multislider_from_query(params, 'speed_pct');
    update_form_multislider_from_query(params, 'crit_rate');
    update_form_multislider_from_query(params, 'crit_damage');
    update_form_multislider_from_query(params, 'resistance');
    update_form_multislider_from_query(params, 'accuracy');

    update_form_multiselect_from_query(params, 'active_sets');

    update_form_select_from_query(params, 'full');
    update_form_select_from_query(params, 'is_grindable');
    update_form_select_from_query(params, 'is_enchantable');

    update_form_toggle_from_query(params, 'full_include_artifacts');
    update_form_toggle_from_query(params, 'active_sets_all');
}

function clean_rune_builds_url_data(data){
    var cleanedParams = clean_query_params(data)
    var params = new URLSearchParams(cleanedParams)
    var multiSliderParams = [
        'avg_efficiency',
        'hp',
        'hp_pct',
        'attack',
        'attack_pct',
        'defense',
        'defense_pct',
        'speed',
        'speed_pct',
        'crit_rate',
        'crit_damage',
        'resistance',
        'accuracy',
    ]
    var newData = clean_multi_slider_min_max_params(params, multiSliderParams)
    return newData
}

function update_rune_builds_inventory() {
    $('#FilterInventoryForm').submit();
}

$('body')
    .on('click', '#FilterInventoryForm :submit', function() {
        var $form = $(this).closest('form');
        $('<input>').attr({
            type: 'hidden',
            id: 'id' + $(this).attr('name'),
            name: $(this).attr('name'),
            value: $(this).attr('value')
        }).appendTo($form);
    })
    .on('submit', '.ajax-form', function() {
        //Handle add ajax form submit
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),
            global: false
        }).done(function(result) {
            if (result.code === 'success') {
                $('.modal.show').modal('hide');
                update_rune_builds_inventory();

                if (result.removeElement) {
                    $(result.removeElement).remove();
                }
            }
            $form.replaceWith(result.html);
            $('.rating').rating();
            $('[data-bs-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.rune-builds-view-mode', function() {
        var view_mode = $(this).data('mode');
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/rune-builds/inventory/' + view_mode + '/',
            global: false
        })
        .done(function(result) {
            update_rune_builds_inventory();
        });
    })
    .on('submit', '#FilterInventoryForm', function() {
        ToggleLoading($('body'), true);

        var $form = $(this);
        var formData = clean_rune_builds_url_data($form.serialize())
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: formData
        }).done(function (data) {
            history.replaceState({}, "", this.url.substring(0, this.url.indexOf('/inventory/')) + '/?' + formData)

            ToggleLoading($('body'), false);
            $('#rune-builds-inventory').replaceWith(data);
            $('#runeBuildsInventoryTable').tablesorter({
                sortReset: true,
                widgets: ['saveSort', 'columnSelector', 'stickyHeaders'],
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
            });
            $('[data-bs-toggle="tooltip"]').tooltip();
        });

        return false;  //cancel default on submit action.
    })
    .on('shown.bs.collapse', '#runeBuildsFilterCollapse', function() {
        $("[data-provide='slider']").slider('relayout');
    })
    .on('click', '.reset', function() {
        $('#runeBuildsInventoryTable').trigger('sortReset');
        var $form = $('#FilterInventoryForm');
        $form[0].reset();

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
        $("input[name='active_stats_all']").prop("checked", false);
        $("input[name='active_stats_all']").parent().addClass('off');

        // Toggle button
        $("input[name='full_include_artifacts']").prop("checked", false);
        $("input[name='full_include_artifacts']").parent().addClass('off');

        update_rune_builds_inventory();
    })
