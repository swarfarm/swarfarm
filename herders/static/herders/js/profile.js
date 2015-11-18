$(document).ready(function() {
    update_monster_inventory();
});

function update_monster_inventory() {
    $('#FilterInventoryForm').submit();
}

function AddMonster() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/add/',
        type: 'get'
    }).done( function(result) {
        bootbox.dialog({
            title: "Add Monster",
            message: result.html
        })
        $('.rating').rating();
    })
}

function EditMonster(instance_id) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/edit/' + instance_id + '/'
    }).done(function(result) {
        bootbox.dialog({
            title: 'Edit Monster',
            message: result.html
        });
        $('.rating').rating();
    });
}

function AwakenMonster(instance_id) {
    if (instance_id) {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/monster/awaken/' + instance_id + '/'
        }).done(function(result) {
            bootbox.dialog({
                title: 'Awaken Monster',
                message: result.html
            });
            $('.rating').rating();
        });
    }
}

function DeleteMonster(instance_id) {
    if (instance_id) {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function (result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/monster/delete/' + instance_id + '/',
                        data: {
                            "delete": "delete",
                            "instance_id": instance_id
                        }
                    }).done(function () {
                        update_monster_inventory();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    }
    else {
        alert("Unspecified monster to delete");
    }
}

function QuickFodder(btn) {
    var monster_id = btn.data('monster-id');
    var stars = btn.data('stars');
    var level = btn.data('level');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/quick_add/' + monster_id.toString() + '/' + stars.toString() + '/' + level.toString() + '/'
    }).done(function() {
        update_monster_inventory();
    });
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
        }).done(function(data) {
            if (data.code === 'success') {
                $('.modal.in').modal('hide');
                update_monster_inventory();
            }
            else {
                $form.replaceWith(data.html);
                $('.rating').rating();
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.monster-add', function() { AddMonster() })
    .on('click', '.monster-edit', function() { EditMonster($(this).data('instance-id')) })
    .on('click', '.monster-delete', function() { DeleteMonster($(this).data('instance-id')) })
    .on('click', '.monster-awaken', function() { AwakenMonster($(this).data('instance-id')) })
    .on('click', '.quick-fodder', function() { QuickFodder($(this)) })
    .on('click', '.profile-view-mode', function() {
        var view_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/monster/inventory/' + view_mode + '/', function() {
            update_monster_inventory();
        });
    })
    .on('click', '.box-group-mode', function() {
        var group_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/monster/inventory/box/' + group_mode + '/', function() {
            update_monster_inventory();
        });
    })
    .on('submit', '#FilterInventoryForm', function() {
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            $('#monster-inventory').replaceWith(data);
        });

        return false;  //cancel default on submit action.
    });