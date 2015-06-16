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
    $('#monster_table').tablesorter({
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

    $('button.filter').click(function() {
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