var element_loading_template = '<div class="spinner-overlay text-center"><div class="spinner spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
var popoverDelay = null;
var autosubmitDelay = null;
var myDefaultAllowList = bootstrap.Tooltip.Default.allowList

//Initialize all bootstrap tooltips and popovers
$(function () {
    // Cancel default focus stuff for modal windows so select2 works properly.
    // Can't set dropdownParent via DAL.
    $.fn.modal.Constructor.prototype.enforceFocus = function () {};

    myDefaultAllowList.div = ['data-rune-id', 'data-artifact-id']

    $('[data-bs-toggle="tooltip"]').tooltip({
        container: 'body'
    });
    $('[data-bs-toggle="popover"]').popover({
        html:true,
        viewport: {selector: 'body', padding: 2}
    });

    $('.rating').rating();

    initSelect();
});

// Various select2 templates for the types of autocompletes
function iconSelect2Template(option) {
    if (option.id) {
        var resource_url = $(option.element).data('image');
        return $('<span><img src="' + resource_url + '" loading="lazy" /> ' + option.text + '</span>');
    }
    else {
        return option.text;
    }
}

// Init all the select2s with the appropriate templates
$.fn.select2.defaults.set("theme", "bootstrap-5");
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

//Defaults for the bootboxes
bootbox.setDefaults({
    backdrop: true,
    closeButton: true,
    animate: true,
    onEscape: true
});

PNotify.prototype.options.styling = "fontawesome";
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



$('body')
    .on('click', '.canvas-slid a', function() {
        $('.navmenu').offcanvas('hide');
    })
    .on('click', '.closeall', function() { $('.panel-collapse.show').collapse('hide'); })
    .on('click', '.openall', function() { $('.panel-collapse:not(".show")').collapse('show'); })
    .on('click', '.data-logs-detach', function() { DetachDataLogs() })
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
                    placement: 'auto',
                    container: '#wrap',
                    viewport: {selector: '#wrap', padding: 2},
                    template: '<div class="monster-skill shadow-lg border-0 popover" role="tooltip"><div class="popover-arrow"></div><h3 class="popover-header fw-lighter"></h3><div class="popover-body"></div></div>'
                });
                if (el.is(":hover")) {
                    el.popover('show');
                }
            });

        }, 250);
    })
    .on('mouseleave', '.skill-popover', function(event) {
        $(this).popover('hide');
        clearTimeout(popoverDelay);
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
    },
    theme: 'bootstrap',
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
