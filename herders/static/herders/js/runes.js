$(document).ready(function() {
    update_rune_inventory();
    update_rune_counts();
});

function update_rune_inventory() {
    $('#FilterInventoryForm').submit();
}

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
            data: $form.serialize()
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
            url: '/profile/' + PROFILE_NAME + '/runes/add/'
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
            url: '/profile/' + PROFILE_NAME + '/runes/edit/' + rune_id + '/'
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
    .on('click', '.rune-delete-all', function() {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure you want to delete <strong>all</strong> of your runes? Your monster rune assignments will be removed as well.',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/all'
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
            url: '/profile/' + PROFILE_NAME + '/runes/import/'
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
            url: '/profile/' + PROFILE_NAME + '/runes/export/'
        }).done(function(result) {
            bootbox.dialog({
                title: "Export Runes and Monsters",
                message: result.html
            });
        })
    })
    .on('click', '.rune-view-mode', function() {
        var view_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/runes/inventory/' + view_mode + '/', function() {
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
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            $('#rune-inventory').replaceWith(data);
        });

        return false;  //cancel default on submit action.
    });