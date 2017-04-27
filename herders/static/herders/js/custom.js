var element_loading_template = '<div class="spinner-overlay"><div class="spinner"></div></div>';
var popoverDelay = null;
var autosubmitDelay = null;

//Initialize all bootstrap tooltips and popovers
$(function () {
    // Cancel default focus stuff for modal windows so select2 works properly.
    // Can't set dropdownParent via DAL.
    $.fn.modal.Constructor.prototype.enforceFocus = function () {};

    $('[data-toggle="tooltip"]').tooltip({
        container: 'body'
    });
    $('[data-toggle="popover"]').popover({
        html:true,
        viewport: {selector: 'body', padding: 2}
    });

    $('.inline-editable').editable();

    $('.rating').rating();

    DisplayMessages();
    initSelect();
});

//x-editable options
$.fn.editable.defaults.container = 'body';

// Various select2 templates for the types of autocompletes
function monsterSelect2Template(option) {
    if (option.id) {
        return $('<span><img src="' + option.image_filename + '" class="monster-inline"/> ' + option.text + '</span>');
    }
    else {
        return option.text;
    }
}

function elementSelect2Template(option) {
    if (option.id) {
        return $('<span><img src="/static/herders/images/elements/' + option.text.toLowerCase() + '.png" /> ' + option.text + '</span>');
    }
    else {
        return option.text;
    }
}

function skillEffectSelect2Template(option) {
    if (option.id) {
        var vals = option.text.split(';'),
            img = vals[0],
            name = vals[1];

        return $('<span><img src="' + img + '" /> ' + name + '</span>');
    }
    else {
        return option.text;
    }
}

// Init all the select2s with the appropriate templates
$.fn.select2.defaults.set("theme", "bootstrap");
$.fn.select2.defaults.set("width", "100%");
$.fn.select2.defaults.set("allowClear", true);
$.fn.select2.defaults.set("escapeMarkup", function(m) {return m;});

function initSelect(baseNode) {
    if (baseNode) {
        baseNode = baseNode.find('.select2');
    }
    else {
        baseNode = $('.select2');
    }

    baseNode.each(function () {
        // Parse out custom select2 configs from data attributes that can't be directly initialized by select2()
        var config = Object();

        // Templates
        var selection_template = window[$(this).data('selection-template')];
        if (typeof selection_template === 'function') {
            config = Object.assign(config, {templateSelection: selection_template});
        }

        var result_template = window[$(this).data('result-template')];
        if (typeof selection_template === 'function') {
            config = Object.assign(config, {templateResult: result_template});
        }

        var parent_selector = $(this).data('select2-parent');
        if (parent_selector) {
            config = Object.assign(config, {dropdownParent: $(parent_selector)});
        }

        $(this).select2(config);
    });
}

// Auto-redirect on click of autocomplete results with URLs
$('#bestiary_quick_search').find('#id_name').on('select2:select', function(event) {
    // Some bullshittery to convert the plain text passed by select2 event into an actual DOM element and extract the data attribute
    var data = $(event.target).select2('data');
    var url = $(data[0].element.innerText).data('redirect-url');

    if (url) {
        window.location.replace(url);
    }
});

$(document).ajaxComplete(function() {
    DisplayMessages();
});

//Defaults for the bootboxes
bootbox.setDefaults({
    backdrop: true,
    closeButton: true,
    animate: true,
    onEscape: true
});

PNotify.prototype.options.styling = "bootstrap3";
PNotify.prototype.options.stack.firstpos1 = 60;
PNotify.prototype.options.stack.spacing1 = 10;


function slugify(text)
{
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}

//Modal management scripts
$('#addMonsterModal').on('shown.bs.modal', function () {
    $('#id_monster-autocomplete').focus()
});

function ToggleLoading(targetElement, setLoadingOn) {
    if (setLoadingOn === undefined) {
        if (targetElement.children('.spinner-overlay').length == 0) {
            targetElement.append(element_loading_template);
        }
        else {
            targetElement.children('.spinner-overlay').remove();
        }
    }
    else {
        if (setLoadingOn && targetElement.children('.spinner-overlay').length == 0) {
            targetElement.append(element_loading_template);
        }
        else if (!setLoadingOn) {
            targetElement.children('.spinner-overlay').remove();
        }
    }
}

//Generate growl notifications
function DisplayMessages() {
    $.ajax({
        url: API_URL + 'messages/',
        type: 'get',
        global: false
    }).done(function(result) {
            for (var i = 0; i < result.messages.length; i++) {
                new PNotify({
                    text: result.messages[i].text,
                    type: result.messages[i].status
                });
            }
        }
    );
}

//Automatically set attributes based on monster info
function SetStars(e) {
    var monster_id = e.params.args.data.id;
    var stars_field = '#' + $(this).data('stars-field');
    var priority_field = '#' + $(this).data('priority-field');
    var fodder_field = '#' + $(this).data('fodder-field');

    // Hit up bestiary API to get monster data
    $.ajax({
        url: API_URL + 'bestiary/' + monster_id + '.json',
        type: 'get',
        global: false
    }).done(function(monster) {
        //Set stars
        if (monster.is_awakened && monster.base_stars > 1) {
            //Awakened is -1 star to get actual base
            $(stars_field).rating('rate', monster.base_stars - 1);
        }
        else {
            $(stars_field).rating('rate', monster.base_stars);
        }

        //Set fodder
        if (monster.archetype === 'Material') {
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

function EssenceStorage() {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/storage/'
    }).done(function(result) {
        bootbox.dialog({
            title: 'Essence Inventory',
            size: 'large',
            message: result.html
        });
    })
}

$('body')
    .on('click', '.canvas-slid a', function() {
        $('.navmenu').offcanvas('hide');
    })
    .on('click', '[data-set-max-level]', SetMaxLevel)
    .on('click', '[data-skill-field]', SetMaxSkillLevel)
    .on('select2:selecting', '[data-set-stars]', SetStars)
    .on('click', '.essence-storage', function() { EssenceStorage() })
    .on('click', '.closeall', function() { $('.panel-collapse.in').collapse('hide'); })
    .on('click', '.openall', function() { $('.panel-collapse:not(".in")').collapse('show'); })
    .on('change switchChange.bootstrapToggle', '.auto-submit', function() {
        clearTimeout(autosubmitDelay);
        var $form = $(this).parents("form");
        autosubmitDelay = setTimeout(function() {
            $form.submit();
        }, 1000);
    })
    .on('hide.bs.modal', function() {
        clearTimeout(autosubmitDelay);
    })
    .on('mouseenter', '.rune-popover', function() {
        var el = $(this);
        popoverDelay = setTimeout(function () {
            var rune_id = el.data('rune-id');

            if (rune_id.length > 0) {
                $.ajax({
                    url: API_URL + 'runes/' + el.data('rune-id') + '.html',
                    type: 'get',
                    global: false
                }).done(function (d) {
                    el.popover({
                        trigger: 'manual',
                        content: d,
                        placement: popoverPlacement(el),
                        html: true,
                        viewport: {selector: '#wrap', padding: 2},
                        container: '#wrap',
                        template: '<div class="rune-stats popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
                    });

                    if (el.is(":hover")) {
                        el.popover('show');
                    }
                });
            }
        }, 250);
    })
    .on('mouseenter', '.monster-popover', function() {
        var el = $(this);
        popoverDelay = setTimeout(function () {
            var url = API_URL + 'instance/' + el.data('instance-id') + '.html';
            $.ajax({
                url: url,
                type: 'get',
                global: false
            }).done(function (d) {
                el.popover({
                    trigger: 'manual',
                    content: d,
                    html: true,
                    placement: popoverPlacement(el),
                    container: 'body',
                    viewport: {selector: 'body', padding: 2},
                    template: '<div class="monster-stats popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
                });

                if (el.is(":hover")) {
                    el.popover('show');
                }
            });
        }, 250);
    })
    .on('mouseenter', '.skill-popover', function() {
        var el = $(this);
        popoverDelay = setTimeout(function () {
            var url = API_URL + 'skill/' + el.data('skill-id') + '.html';
            $.ajax({
                url: url,
                type: 'get',
                global: false
            }).done(function (d) {
                el.popover({
                    trigger: 'manual',
                    content: d,
                    html: true,
                    placement: popoverPlacement(el),
                    container: '#wrap',
                    viewport: {selector: '#wrap', padding: 2},
                    template: '<div class="monster-skill popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
                });
                if (el.is(":hover")) {
                    el.popover('show');
                }
            });

        }, 250);
    })
    .on('mouseleave', '.skill-popover, .monster-popover, .rune-popover', function(event) {
        $(this).popover('hide');
        clearTimeout(popoverDelay);
    })
    .on('click', 'input[type=reset]', function() {
        var $form = $(this).parents('form');
        $form[0].reset();
        $form.find('label.btn').toggleClass('active', false);
        $form.submit();
        return false;
    });

function popoverPlacement(element) {
    var windowWidth = jQuery(window).width(),
        elWidth = element.width(),
        elDistanceFromRight = windowWidth - (element.offset().left + elWidth);

    if (windowWidth - elWidth < 250) {
        return 'auto top';
    }
    else if (elDistanceFromRight < 500) {
        return 'auto left';
    }
    else {
        return 'auto right';
    }
}

//Bulk add
$('#bulkAddFormset').formset({
        animateForms: false
    }).on('formAdded', function() {
    $('.rating').rating();
});

//Update filter buttons on page load
var monster_table = $('#bestiary_table');
var filter_buttons = $('button.filter');
var active_filter_class = 'active';
var save_filters = monster_table.data('save-filters');

monster_table.tablesorter({
    widgets: ['filter', 'saveSort'],
    ignoreCase: true,
    widgetOptions: {
        filter_columnFilters: true,
        filter_reset: 'button.reset',
        filter_external : '.search',
        filter_ignoreCase : true,
        filter_liveSearch : true,
        filter_searchDelay : 300,
        filter_saveFilters : save_filters,
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

    var filters = monster_table.find('input.tablesorter-filter'),
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
    monster_table.trigger('saveSortReset').trigger("sortReset");
});

//Rune form common functions
function update_main_slot_options(slot, main_stat_input) {
    $.ajax({
        type: 'get',
        url: API_URL + 'runes/stats_by_slot/' + slot.toString() + '/'
    }).done(function (response) {
        if (response.code === 'success') {
            // Record the current stat to see if we can pick it in the new list
            var current_stat = main_stat_input.val();

            main_stat_input.empty();
            $.each(response.data, function (val, text) {
                main_stat_input.append(
                    $('<option></option>').val(val).html(text)
                );
            });

            var exists = 0 != main_stat_input.find("option[value='"+current_stat+"']").length;
            if (exists) {
                main_stat_input.val(current_stat);
            }
            else {
                for(var key in response.data) break;
                main_stat_input.val(key);
            }
        }
    });
}

function update_main_stat_value(stat, grade, level, main_stat_value_element) {
    main_stat_value_element.val(RUNE_MAIN_STAT_VALUES[stat][grade][level]);
}

function update_craft_stat_options(craft, stat_input) {
    $.ajax({
        type: 'get',
        url: API_URL + 'runes/stats_by_craft/' + craft.toString() + '/'
    }).done(function (response) {
        if (response.code === 'success') {
            // Record the current stat to see if we can pick it in the new list
            var current_stat = stat_input.val();

            stat_input.empty();
            $.each(response.data, function (val, text) {
                stat_input.append(
                    $('<option></option>').val(val).html(text)
                );
            });

            var exists = 0 != stat_input.find("option[value='"+current_stat+"']").length;
            if (exists) {
                stat_input.val(current_stat);
            }
            else {
                for(var key in response.data) break;
                stat_input.val(key);
            }
        }
    });
}

const RUNE_MAIN_STAT_VALUES = {
  "1": {
    "1": [40, 85, 130, 175, 220, 265, 310, 355, 400, 445, 490, 535, 580, 625, 670, 804],
    "2": [70, 130, 190, 250, 310, 370, 430, 490, 550, 610, 670, 730, 790, 850, 910, 1092],
    "3": [100, 175, 250, 325, 400, 475, 550, 625, 700, 775, 850, 925, 1000, 1075, 1150, 1380],
    "4": [160, 250, 340, 430, 520, 610, 700, 790, 880, 970, 1060, 1150, 1240, 1330, 1420, 1704],
    "5": [270, 375, 480, 585, 690, 795, 900, 1005, 1110, 1215, 1320, 1425, 1530, 1635, 1740, 2088],
    "6": [360, 480, 600, 720, 840, 960, 1080, 1200, 1320, 1440, 1560, 1680, 1800, 1920, 2040, 2448]
  },
  "2": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
    "4": [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
    "5": [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
    "6": [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63]
  },
  "3": {
    "1": [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
    "2": [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
    "3": [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
    "4": [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
    "5": [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
    "6": [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160]
  },
  "4": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
    "4": [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
    "5": [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
    "6": [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63]
  },
  "5": {
    "1": [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
    "2": [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
    "3": [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
    "4": [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
    "5": [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
    "6": [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160]
  },
  "6": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
    "4": [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
    "5": [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
    "6": [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63]
  },
  "7": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 25],
    "4": [4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 30],
    "5": [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 39],
    "6": [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 42]
  },
  "8": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
    "4": [4, 6, 8, 11, 13, 15, 17, 19, 22, 24, 26, 28, 30, 33, 35, 41],
    "5": [5, 7, 10, 12, 15, 17, 19, 22, 24, 27, 29, 31, 34, 36, 39, 47],
    "6": [7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 58]
  },
  "9": {
    "1": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "2": [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
    "3": [4, 6, 9, 11, 13, 16, 18, 20, 22, 25, 27, 29, 32, 34, 36, 43],
    "4": [6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 57],
    "5": [8, 11, 15, 18, 21, 25, 28, 31, 34, 38, 41, 44, 48, 51, 54, 65],
    "6": [11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67, 80]
  },
  "10": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
    "4": [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
    "5": [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
    "6": [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64]
  },
  "11": {
    "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
    "2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
    "3": [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
    "4": [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
    "5": [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
    "6": [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64]
  }
};

const RUNE_SUBSTAT_MAX_VALUES = {"1": 1250, "2": 40.0, "3": 125, "4": 40.0, "5": 125, "6": 40.0, "7": 30.0, "8": 30.0, "9": 35.0, "10": 40.0, "11": 40.0};