// Rune functions
function AssignRune(slot) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/assign/' + INSTANCE_ID + '/' + slot.toString() + '/'
    }).done(function (response) {
       bootbox.dialog({
            title: "Assign Rune",
            message: response.html
        });
        $('.rating').rating();
        $('.modal.in').modal('handleUpdate');
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
    $('.modal.in').modal('hide');
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
        $('.modal.in').modal('handleUpdate');
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
    }).done(function(result) {
        bootbox.dialog({
            title: "Edit rune",
            message: result.html
        });
        update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
        $('.rating').rating();
    });
}

// Monster edit functions
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

function DeleteMonster(instance_id) {
    if (instance_id) {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'post',
                        url: '/profile/' + PROFILE_NAME + '/monster/delete/' + instance_id + '/',
                        data: {
                            "delete": "delete",
                            "instance_id": instance_id
                        }
                    }).done(function () {
                        location.href= '/profile/' + PROFILE_NAME + '/'
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

// Page update functions
function UpdateSidebar() {
    $('#monster-view-sidebar').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/sidebar/');
}

function UpdateRunes() {
    $('#monster-view-runes').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/runes/', function() {
        $('.popover').remove();
    });
}

function UpdateStats() {
    $('#monster-view-stats').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/stats/')
}

function UpdateSkills() {
    $('#monster-view-skills').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/skills/', function() {
        $('[data-toggle="popover"]').popover({
            html:true
        });
    })
}

function UpdateNotes() {
    $('#monster-view-notes-info').load('/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/info/')
}

function UpdateAll() {
    UpdateSidebar();
    UpdateRunes();
    UpdateStats();
    UpdateSkills();
    UpdateNotes();
}

$(document).ready(UpdateAll());

// Event ties
$('body')
    .on('click', '.rune-edit', function() { EditRune($(this).data('rune-id')) })
    .on('click', '.rune-unassign', function() { UnassignRune($(this).data('rune-id')) })
    .on('click', '.rune-assign', function() { AssignRune($(this).data('rune-slot')) })
    .on('click', '.rune-assign-choice', function() { AssignRuneChoice($(this).data('rune-id'), $(this).data('instance-id')) })
    .on('click', '.monster-edit', function() { EditMonster($(this).data('instance-id')) })
    .on('click', '.monster-delete', function() { DeleteMonster($(this).data('instance-id')) })
    .on('click', '.monster-awaken', function() { AwakenMonster($(this).data('instance-id')) })
    .on('click', '#addNewRune', function() { CreateNewRune($("#id_slot").val()) })
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