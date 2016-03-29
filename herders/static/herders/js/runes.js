$(document).ready(function() {
    update_rune_inventory();
    update_rune_counts();
});

function update_rune_inventory() {
    $('#FilterInventoryForm').submit();
}

$('.container').click(function() {
    $('.collapse.in').collapse('hide');
});

$('body')
    .on('click', ':submit', function() {
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
                update_rune_counts();

                if (result.removeElement) {
                    $(result.removeElement).remove();
                }
            }
            $form.replaceWith(result.html);
            $('.rating').rating();
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
                message: data.html
            });

            update_main_slot_options($('#id_slot').val(), $('#id_main_stat'));
            $('.rating').rating();
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
                message: data.html
            });
            update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
            $('.rating').rating();
        });
    })
    .on('click', '.rune-delete', function() {
        //Pull in delete confirmation form on modal show
        var rune_id = $(this).data('rune-id');

        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/' + rune_id + '/',
                        data: {
                            "delete": "delete",
                            "rune_id": rune_id
                        }
                    }).done(function () {
                        update_rune_inventory();
                        update_rune_counts();
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
            message: 'Are you sure you want to delete <strong>all</strong> of your runes? Your monster rune assignments will be removed as well.',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/all',
                        global: false
                    }).done(function() {
                        update_rune_inventory();
                        update_rune_counts();
                    }).fail(function() {
                        alert("Something went wrong! Server admin has been notified.");
                    })
                }
            }
        })
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
            ToggleLoading($('body'), false);
            $('#rune-inventory').replaceWith(data);
            $('#runeInventoryTable').tablesorter({
                widgets: ['saveSort', 'stickyHeaders'],
                widgetOptions: {
                    filter_reset: '.reset',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 100
                }
            });
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.reset', function() {
        $('#runeInventoryTable').trigger('sortReset');
        var form = $('#FilterInventoryForm');
        form[0].reset();
        form.find('label').toggleClass('active', false);
        update_rune_inventory();
    })
    .on('click', '.box-group-mode', function() {
        var group_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/runes/inventory/box/' + group_mode + '/', function() {
            update_rune_inventory();
        });
    });