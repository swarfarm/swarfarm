//Initialize all bootstrap tooltips and popovers
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover({
        html:true
    });
});

//Defaults for the bootboxes
bootbox.setDefaults({
    backdrop: true,
    closeButton: true,
    animate: true,
    onEscape: true
});

//Custom popovers for loading AJAX content
$('*[data-instance-id]').hover(function(event) {
    if (event.type === 'mouseenter') {
        var el = $(this);
        var url = API_URL + 'instance/' + el.data('instance-id') + '.html';
        $.get(url, function (d) {
            el.popover({
                trigger: 'manual',
                content: d,
                html: true,
                container: 'body',
                template: '<div class="monster-stats popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
            });

            if (el.is(":hover")) {
                el.popover('show');
            }
        });
    } else {
        $(this).popover('hide');
    }
});

//Modal management scripts
$('#addMonsterModal').on('shown.bs.modal', function () {
    $('#id_monster-autocomplete').focus()
});

// Monster view page show modals on load
$(window).load(function() {
    var hashStr = location.hash.replace("#","");
    if (hashStr) {
        switch(hashStr) {
            case 'edit':
                $('#editMonsterModal').modal('show');
                break;
            case 'awaken':
                $('#awakenMonsterModal').modal('show');
                break;
        }
    }
});

//Automatically set attributes based on monster info
function SetStars(e, choice, autocomplete) {
    var monster_id = choice[0].dataset['value'];
    var stars_field = '#' + $(this).data('stars-field');
    var priority_field = '#' + $(this).data('priority-field');
    var fodder_field = '#' + $(this).data('fodder-field');
    var url = API_URL + 'bestiary/' + monster_id + '.json';

    $.ajax({
        url: url
    }).done(function (result) {
        //Set stars
        if (result.is_awakened && result.base_stars > 1) {
            //Awakened is -1 star to get actual base
            $(stars_field).rating('rate', result.base_stars - 1);
        }
        else {
            $(stars_field).rating('rate', result.base_stars);
        }

        //Set fodder
        if (result.archetype == 'material') {
            $(priority_field).val('0');
            $(fodder_field).prop('checked', true);
        }
    });
}

//Calculate max level based on stars currently entered
function SetMaxLevel() {
    var stars_field = '#' + $(this).data('stars-field');
    var level_field = '#' + $(this).data('level-field');
    var stars = $(stars_field).val();
    $(level_field).val(10 + stars * 5);
}
//Set max skill level
function SetMaxSkillLevel() {
    var skill_level_field = $('#' + $(this).data('skill-field'));
    var maxlv = skill_level_field.attr('max');
    skill_level_field.val(maxlv)
}

$('body').on('click', '*[data-set-max-level]', SetMaxLevel)
    .on('click', '*[data-skill-field]', SetMaxSkillLevel)
    .on('selectChoice', '*[data-set-stars]', SetStars)
    .on('click', '.closeall', function() { $('.panel-collapse.in').collapse('hide'); })
    .on('click', '.openall', function() { $('.panel-collapse:not(".in")').collapse('show'); });


//Bulk add
$('#bulkAddFormset').formset({
        animateForms: false
    }).on('formAdded', function() {
    $('.rating').rating();
});

//Update filter buttons on page load
var monster_table = $('#monster_table');
var filter_buttons = $('button.filter');
var active_filter_class = 'active';

monster_table.tablesorter({
    widgets: ['filter', 'saveSort'],
    ignoreCase: true,
    widthFixed: true,
    widgetOptions: {
        filter_columnFilters: true,
        filter_reset: 'button.reset',
        filter_external : '.search',
        filter_ignoreCase : true,
        filter_liveSearch : true,
        filter_searchDelay : 300,
        filter_saveFilters : true,
        filter_searchFiltered : true
    }
});

//Get list of current filters and set buttons properly
var current_filters;

if (monster_table.length > 0) {
    current_filters = $.tablesorter.getFilters(monster_table);

    if (current_filters) {
        filter_buttons.each(function () {
            var filter_col = $(this).data('filter-column'),
                filter_text = $(this).data('filter-text'),
                filter_function = $(this).data('filter-function'),
                mult = current_filters[filter_col].split(filter_function);

            if ($.inArray(String(filter_text), mult) > -1) {
                $(this).toggleClass(active_filter_class, true);
            }
        });
    }
}

//Toggle text in filter field when button is pressed
filter_buttons.click(function() {
    $( this ).toggleClass(active_filter_class);

    var filters = $('#monster_table').find('input.tablesorter-filter'),
        col = $(this).data('filter-column'),
        filter_txt = $(this).data('filter-text'),
        filter_function = $(this).data('filter-function'),
        exclusive = $(this).data('filter-exclusive'),
        current_filters = filters.eq(col).val(),
        mult, i;

    if (!filter_function) {
        filter_function = '|';
    }

    if (current_filters && filter_txt !== '') {
        mult = current_filters.split(filter_function);
        i = $.inArray(String(filter_txt), mult);
        if (exclusive) {
            if (i >= 0) {
                filter_txt = '';
            } else {
                // Remove pressed status of other buttons assigned to same col
                $('[data-filter-column="' + String(col) + '"]').toggleClass(active_filter_class, false);
                $(this).toggleClass(active_filter_class, true);
            }
        }
        else {
            if (i < 0) {
            mult.push(String(filter_txt));
            } else {
                mult.splice(String(i),1);
            }
            filter_txt = mult.join(filter_function);
        }
    }
    filters.eq(col).val(filter_txt).trigger('search', false);
});

//Reset filters
$('button.reset').click(function() {
    $('button.filter').toggleClass(active_filter_class, false);
    $('#monster_table').trigger('saveSortReset').trigger("sortReset");
});
