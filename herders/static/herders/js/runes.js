$(document).ready(function() {
    update_rune_form_with_query();
    update_rune_inventory();
});

function update_rune_form_with_query(){
    var params = new URLSearchParams(location.search)
    
    update_form_multislider_from_query(params, 'stars');
    update_form_multislider_from_query(params, 'has_grind');
    update_form_multislider_from_query(params, 'level');

    update_form_multiselect_from_query(params, 'type');
    update_form_multiselect_from_query(params, 'slot');
    update_form_multiselect_from_query(params, 'main_stat');
    update_form_multiselect_from_query(params, 'innate_stat');
    update_form_multiselect_from_query(params, 'substats');
    update_form_multiselect_from_query(params, 'quality');
    update_form_multiselect_from_query(params, 'original_quality');

    update_form_select_from_query(params, 'ancient');
    update_form_select_from_query(params, 'has_gem');
    update_form_select_from_query(params, 'assigned_to');
    update_form_select_from_query(params, 'marked_for_sale');
    update_form_select_from_query(params, 'is_grindable');
    update_form_select_from_query(params, 'is_enchantable');

    update_form_radio_from_query(params, 'fodder');
    update_form_radio_from_query(params, 'in_storage');
    update_form_radio_from_query(params, 'monster__fusion_food');

    update_form_toggle_from_query(params, 'substat_logic');
    update_form_toggle_from_query(params, 'substat_reverse');
}

function update_rune_inventory() {
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
                $('.modal.in').modal('hide');
                update_rune_inventory();

                if (result.removeElement) {
                    $(result.removeElement).remove();
                }
            }
            $form.replaceWith(result.html);
            $('.rating').rating();
            $('[data-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.rune-add', function() {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/add/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Add rune",
                size: "large",
                message: data.html
            });

            update_main_slot_options($('#id_slot').val(), $('#id_main_stat'));
            $('.rating').rating();
        });
    })
    .on('click', '.rune-craft-add', function() {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/craft/add/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Add Grindstone/Gem",
                message: data.html
            });
        });
    })
    .on('click', '.rune-edit', function() {
        //Pull in edit form on modal show
        var rune_id = $(this).data('rune-id');

        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/edit/' + rune_id + '/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Edit rune",
                size: "large",
                message: data.html
            });
            update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
            $('.rating').rating();
        });
    })
    .on('click', '.rune-craft-edit', function() {
        //Pull in edit form on modal show
        var craft_id = $(this).data('craft-id');

        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/craft/edit/' + craft_id + '/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Edit Grindstone/Gem",
                message: data.html
            });
            update_craft_stat_options($('#id_type').val(), $('#id_stat'));
        });
    })
    .on('click', '.rune-delete', function() {
        //Pull in delete confirmation form on modal show
        var craft_id = $(this).data('rune-id');

        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/' + craft_id + '/',
                        data: {
                            "delete": "delete",
                            "rune_id": craft_id
                        }
                    }).done(function () {
                        update_rune_inventory();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    })
    .on('click', '.rune-craft-delete', function() {
        //Pull in delete confirmation form on modal show
        var craft_id = $(this).data('craft-id');

        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/craft/delete/' + craft_id + '/',
                        data: {
                            "delete": "delete",
                            "rune_id": craft_id
                        }
                    }).done(function () {
                        update_rune_inventory();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    })
    .on('click', '.rune-unassign-all', function() {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure you want to unassign <strong>all</strong> of your runes? This process might take a few seconds.',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/unassign/all',
                        global: false
                    }).done(function() {
                        update_rune_inventory();
                    }).fail(function() {
                        alert("Something went wrong! Server admin has been notified.");
                    })
                }
            }
        })
    })
    .on('click', '.rune-delete-all', function() {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure you want to delete <strong>all</strong> of your runes, grindstones, and enchant gems? Your monster rune assignments will be removed as well.',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/all',
                        global: false
                    }).done(function() {
                        update_rune_inventory();
                    }).fail(function() {
                        alert("Something went wrong! Server admin has been notified.");
                    })
                }
            }
        })
    })
    .on('click', '.rune-delete-notes-all', function() {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure you want to delete notes from <strong>all</strong> of your runes?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete-notes',
                        global: false
                    }).done(function() {
                        update_rune_inventory();
                    }).fail(function() {
                        alert("Something went wrong! Server admin has been notified.");
                    })
                }
            }
        })
    })
    .on('click', '.rune-resave-all', function() {
        bootbox.confirm(
            'The data structure for saving runes was changed and your runes need to be updated so the filters work properly. Click OK to start saving the runes. This process may take a minute or two depending on how many runes you own.',
            function(result) {
                if (result) {
                    ToggleLoading($('body'), true);
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/resave/all/',
                        global: false
                    }).done(function() {
                        location.reload();
                    }).fail(function() {
                        alert("Something went wrong! Server admin has been notified.");
                        ToggleLoading($('body'), false);
                    })
                }
            }
        )
    })
    .on('click', '.rune-import', function() {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/import/',
            global: false
        }).done(function(result) {
            bootbox.dialog({
                title: "Import Runes",
                message: result.html
            });
        })
    })
    .on('click', '.rune-export', function() {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/export/',
            global: false
        }).done(function(result) {
            bootbox.dialog({
                title: "Export Runes and Monsters",
                message: result.html
            });
        })
    })
    .on('click', '.rune-view-mode', function() {
        var view_mode = $(this).data('mode');
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/runes/inventory/' + view_mode + '/',
            global: false
        })
        .done(function(result) {
            update_rune_inventory();
        });
    })
    .on('change', '#edit_id_slot', function() {
        update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
    })
    .on('change', '#id_slot', function() {
        update_main_slot_options($('#id_slot').val(), $('#id_main_stat'));
    })
    .on('change', '#id_stars, #id_level, #id_main_stat', function() {
        var stat = $('#id_main_stat').val();
        var grade = $('#id_stars').val();
        var level = $('#id_level').val();

        if (stat && grade && level) {
            update_main_stat_value(stat, grade, level, $('#id_main_stat_value'));
        }

    })
    .on('change', '#edit_id_stars, #edit_id_level, #edit_id_main_stat', function() {
        var stat = $('#edit_id_main_stat').val();
        var grade = $('#edit_id_stars').val();
        var level = $('#edit_id_level').val();

        if (stat && grade && level) {
            update_main_stat_value(stat, grade, level, $('#edit_id_main_stat_value'));
        }
    })
    .on('change', '#id_type', function() {
        update_craft_stat_options($('#id_type').val(), $('#id_stat'));
    })
    .on('change', '#filter_id_stars__gte', function() {
        var min_stars = $(this).val();
        var max_stars_field = $('#filter_id_stars__lte');
        if (min_stars > max_stars_field.val()) {
            max_stars_field.rating('rate', min_stars);
        }
        $(this).parents("form").submit();
    })
    .on('change', '#filter_id_stars__lte', function() {
        var max_stars = $(this).val();
        var min_stars_field = $('#filter_id_stars__gte');
        if (max_stars < min_stars_field.val()) {
            min_stars_field.rating('rate', max_stars);
        }
        $(this).parents("form").submit();
    })
    .on('submit', '#FilterInventoryForm', function() {
        ToggleLoading($('body'), true);

        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            // Create URL with Filter fields
            var params_start = this.url.lastIndexOf('/?')
            if (params_start > -1){
                var index_start = Math.min(params_start + 2, this.url.length - 1) // +2 because /? are 2 symbols
                var params = clean_query_params(this.url.substring(index_start))
                $("#idapply").remove() // Apply button adds something to data :/
                history.replaceState({}, "", this.url.substring(0, this.url.indexOf('/inventory/')) + '/?' + params)
            }
            //

            ToggleLoading($('body'), false);
            $('#rune-inventory').replaceWith(data);
            $('#runeInventoryTable').tablesorter({
                widgets: ['saveSort', 'stickyHeaders'],
                widgetOptions: {
                    filter_reset: '.reset',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 50
                }
            });
            $('[data-toggle="tooltip"]').tooltip();
        });

        return false;  //cancel default on submit action.
    })
    .on('shown.bs.collapse', '#runeFilterCollapse', function() {
        $("[data-provide='slider']").slider('relayout');
    })
    .on('click', '.reset', function() {
        $('#runeInventoryTable').trigger('sortReset');
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
        $("input[name='substat_logic']").prop("checked", false);
        $("input[name='substat_logic']").parent().addClass('off');

        update_rune_inventory();
    })
    .on('click', '.box-group-mode', function() {
        var group_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/runes/inventory/box/' + group_mode + '/', function() {
            update_rune_inventory();
        });
    });