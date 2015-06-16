var api_url = 'https://swarfarm.com/api/';

//Initialize all bootstrap tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

//Modal management scripts
$('#addMonsterModal').on('shown.bs.modal', function () {
    $('#id_monster-autocomplete').focus()
});

//Set the star rating upon selecting a monster from autocomplete
$('#id_monster-autocomplete').bind('selectChoice',
    function(e, choice, autocomplete) {
        var monster_id = choice[0].dataset['value'];

        $.getJSON(api_url + 'bestiary/' + monster_id, function(result){
            $('#id_stars').rating('rate', result[0].fields['base_stars']);
        });
    });

$(document).ready(function() {
    var monster_table = $('#monster_table');

    var filter_buttons = $('button.filter');

    var element_filter_col = 4;
    var archetype_filter_col = 5;
    var priority_filter_col = 6;


    monster_table.tablesorter({
        widgets: ['filter', 'saveSort'],
        ignoreCase: true,
        widgetOptions: {
            filter_columnFilters: true,
            filter_reset: 'button.filterreset',
            filter_ignoreCase : true,
            filter_liveSearch : true,
            filter_searchDelay : 300,
            filter_saveFilters : true
        }
    });

    //Get list of current filters
    var current_filters = $.tablesorter.getFilters(monster_table);

    if (current_filters) {
        //Element buttons
        if (current_filters[element_filter_col].includes("fire")){
            $(filter_buttons.get(0)).toggleClass('active', true);
        }

        if (current_filters[element_filter_col].includes("water")){
            $(filter_buttons.get(1)).toggleClass('active', true);
        }

        if (current_filters[element_filter_col].includes("wind")){
            $(filter_buttons.get(2)).toggleClass('active', true);
        }

        if (current_filters[element_filter_col].includes("dark")){
            $(filter_buttons.get(3)).toggleClass('active', true);
        }

        if (current_filters[element_filter_col].includes("light")){
            $(filter_buttons.get(4)).toggleClass('active', true);
        }

        //Archetype buttons
        if (current_filters[archetype_filter_col].includes("Attack")){
            $(filter_buttons.get(5)).toggleClass('active', true);
        }

        if (current_filters[archetype_filter_col].includes("Defense")){
            $(filter_buttons.get(6)).toggleClass('active', true);
        }

        if (current_filters[archetype_filter_col].includes("Hp")){
            $(filter_buttons.get(7)).toggleClass('active', true);
        }

        if (current_filters[archetype_filter_col].includes("Support")){
            $(filter_buttons.get(8)).toggleClass('active', true);
        }

        if (current_filters[archetype_filter_col].includes("Material")){
            $(filter_buttons.get(9)).toggleClass('active', true);
        }

        //Priority buttons
        if (current_filters[priority_filter_col].includes("High")){
            $(filter_buttons.get(10)).toggleClass('active', true);
        }

        if (current_filters[priority_filter_col].includes("Medium")){
            $(filter_buttons.get(11)).toggleClass('active', true);
        }

        if (current_filters[priority_filter_col].includes("Low")){
            $(filter_buttons.get(12)).toggleClass('active', true);
        }

        if (current_filters[priority_filter_col].includes("Done")){
            $(filter_buttons.get(13)).toggleClass('active', true);
        }
    }


    filter_buttons.click(function() {
        $( this ).toggleClass('active');

        var filters = $('#monster_table').find('input.tablesorter-filter'),
            col = $(this).data('filter-column'),
            txt = $(this).data('filter-text'),
            cur = filters.eq(col).val(),
            mult, i;

        if (cur && txt !== '') {
            mult = cur.split('|');
            i = $.inArray(txt, mult);
            if (i < 0) {
                mult.push(txt);
            } else {
                mult.splice(i,1);
            }
            txt = mult.join('|');
        }
        filters.eq(col).val(txt).trigger('search', false);
    });

    $('button.filterreset').click(function() {
        $('button.filter').toggleClass('active', false);
    });

    $('button.sortreset').click(function() {
        $('#monster_table').trigger('saveSortReset').trigger("sortReset");
    });
});