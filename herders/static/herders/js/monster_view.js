// Rune functions
function AssignRune(slot) {
    bootbox.dialog({
        message: 'Assign an existing rune or create a new one?',
        title: 'Assign Rune',
        size: 'small',
        buttons: {
            assign: {
                label: 'Assign Existing',
                className: 'btn-default pull-left',
                callback: function() {
                    AssignExistingRune(slot)
                }
            },
            create_new: {
                label: 'Create New',
                className: 'btn-default',
                callback: function() {
                    CreateNewRune(slot)
                }
            }
        }
    })
}

function AssignExistingRune(slot) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/assign/' + INSTANCE_ID + '/' + slot.toString() + '/'
    }).done(function (response) {
       bootbox.dialog({
            title: "Assign Rune",
            message: response.html
        });
        $('.rating').rating();
    });
}

function AssignRuneChoice(rune_id, monster_id) {

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/assign/' + monster_id + '/' + rune_id + '/'
    }).done(function (response) {
        if (response.code === 'success') {
            $('.modal.in').modal('hide');
            UpdateRunes();
            UpdateStats();
        }
        else {
            alert('Something went wrong assigning the rune :(');
        }
    })
}

function CreateNewRune(slot) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/add/?slot=' + slot.toString() + '&assigned_to=' + INSTANCE_ID
    }).done(function (response) {
       bootbox.dialog({
            title: "Add new rune",
            message: response.html
        });
        update_main_slot_options($('#id_slot').val(), $('#id_main_stat'));
        $('.rating').rating();
    });
}

function UnassignRune(rune_id) {
    bootbox.dialog({
        message: 'Remove from slot or delete completely?',
        title: 'Remove Rune',
        size: 'small',
        buttons: {
            unassign: {
                label: 'Remove from Slot',
                className: 'btn-default pull-left',
                callback: function () {
                    $.ajax({
                        type: 'post',
                        url: '/profile/' + PROFILE_NAME + '/runes/unassign/' + rune_id + '/'
                    }).done(function (response) {
                        if (response.code === 'success') {
                            $('tr[data-rune-id]').popover('hide');
                            UpdateRunes();
                            UpdateStats();
                        }
                    });
                }
            },
            delete: {
                label: 'Delete',
                className: 'btn-danger',
                callback: function () {
                    $.ajax({
                        type: 'post',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/' + rune_id + '/',
                        data: {
                            "delete": "delete",
                            "rune_id": rune_id
                        }
                    }).done(function () {
                        $('tr[data-rune-id]').popover('hide');
                        UpdateRunes();
                        UpdateStats();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        }
    });
}

function EditRune(rune_id) {
    //Pull in edit form on modal show
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
}

// Page update functions
function UpdateRunes() {
    $('#monster-view-runes').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/runes/');
    $('.popover').remove();
}

function UpdateStats() {
    $('#monster-view-stats').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/stats/')
}

function UpdateSkills() {
    $('#monster-view-skills').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/skills/')
}

function UpdateNotes() {
    $('#monster-view-notes-info').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/info/')
}

function UpdateAll() {
    UpdateRunes();
    UpdateStats();
    UpdateSkills();
    UpdateNotes();
}

$(document).ready(UpdateAll);

// Event ties
$('body')
    .on('click', '.rune-edit', function() { EditRune($(this).data('rune-id')) })
    .on('click', '.rune-unassign', function() { UnassignRune($(this).data('rune-id')) })
    .on('click', '.rune-assign', function() { AssignRune($(this).data('rune-slot')) })
    .on('click', '.rune-assign-choice', function() { AssignRuneChoice($(this).data('rune-id'), $(this).data('instance-id')) })
    .on('submit', '#AssignRuneForm', function() {
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            if (data.code === 'results') {
                $('#assign_rune_results').replaceWith(data.html)
            }
            else {
                alert('Unable to retrieve search results :(')
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('submit', '.ajax-form', function() {
        //Handle add ajax form submit
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            if (data.code === 'success') {
                $('.modal.in').modal('hide');
                UpdateAll();
            }
            $form.replaceWith(data.html);
            $('.rating').rating();
        });

        return false;  //cancel default on submit action.
    });