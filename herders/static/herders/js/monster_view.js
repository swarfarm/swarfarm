var rune_dialog;

// Rune functions
function AssignRune(slot) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/assign/' + INSTANCE_ID + '/' + slot.toString() + '/'
    }).done(function (response) {
        rune_dialog = bootbox.dialog({
            title: "Assign Rune",
            size: "large",
            message: response.html
        });

        //Init form elements
        $("[data-bs-toggle='toggle']").bootstrapToggle();
        $("[data-provide='slider']").slider();
        initSelect();
        $('[data-bs-toggle="tooltip"]').tooltip({
            container: 'body'
        });
        $('[data-bs-toggle="popover"]').popover({
            html:true,
            viewport: {selector: 'body', padding: 2}
        });
    });
}

function AssignRuneChoice(rune_id, monster_id) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/assign/' + monster_id + '/' + rune_id + '/'
    }).done(function (response) {
        if (response.code === 'success') {
            $('.modal.show').modal('hide');
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
        if (rune_dialog) {
            $('.bootbox-body').html(response.html)
        }
        else {
            rune_dialog = bootbox.dialog({
                title: "Add new rune",
                size: "large",
                message: response.html
            });

            update_main_slot_options($('#id_slot').val(), $('#id_main_stat'));
            $('.rating').rating();
            rune_dialog.modal('handleUpdate');
        }
    });
}

function UnassignRune(rune_id) {
    $('.rune-stats').popover('hide');
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
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/unassign/' + rune_id + '/',
                        global: false
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
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/runes/delete/' + rune_id + '/',
                        global: false,
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

function RemoveAllRunes(instance_id) {
    if (instance_id) {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/monster/remove_runes/' + instance_id + '/',
                    }).done(function () {
                        UpdateRunes();
                        UpdateStats();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    }
    else {
        alert("Unspecified monster to remove runes & artifacts from!");
    }
}

function EditRune(rune_id) {
    $('.rune-stats').popover('hide');
    //Pull in edit form on modal show
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/edit/' + rune_id + '/'
    }).done(function(result) {
        bootbox.dialog({
            title: "Edit rune",
            size: "large",
            message: result.html
        });
        update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
        $('.rating').rating();
    });
}

// Artifact functions
function AssignArtifact(slot) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/artifacts/assign/' + INSTANCE_ID + '/' + slot.toString() + '/'
    }).done(function (response) {
        rune_dialog = bootbox.dialog({
            title: "Assign Artifact",
            size: "large",
            message: response.html
        });

        //Init form elements
        $("[data-bs-toggle='toggle']").bootstrapToggle();
        $("[data-provide='slider']").slider();
        initSelect();
        $('[data-bs-toggle="tooltip"]').tooltip({
            container: 'body'
        });
        $('[data-bs-toggle="popover"]').popover({
            html:true,
            viewport: {selector: 'body', padding: 2}
        });
    });
}

function AssignArtifactChoice(artifact_id, monster_id) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/artifacts/assign/' + monster_id + '/' + artifact_id + '/'
    }).done(function (response) {
        if (response.code === 'success') {
            $('.modal.show').modal('hide');
            UpdateRunes();
            UpdateStats();
        }
        else {
            alert('Something went wrong assigning the artifact :(');
        }
    })
}

function EditArtifact(artifact_id) {
    $('.rune-stats').popover('hide');
    //Pull in edit form on modal show
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/artifacts/edit/' + artifact_id + '/'
    }).done(function(result) {
        bootbox.dialog({
            title: "Edit artifact",
            size: "large",
            message: result.html
        });
        update_artifact_slot_visibility();
    });
}

function CreateNewArtifact(slot) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/artifacts/add/?slot=' + slot + '&assigned_to=' + INSTANCE_ID,
    }).done(function (response) {
        if (rune_dialog) {
            $('.bootbox-body').html(response.html)
        }
        else {
            rune_dialog = bootbox.dialog({
                title: "Add new artifact",
                size: "large",
                message: response.html
            });
        }

        update_artifact_slot_visibility();
    });
}

function UnassignArtifact(artifact_id) {
    $('.rune-stats').popover('hide');
    bootbox.dialog({
        message: 'Remove from slot or delete completely?',
        title: 'Remove Artifact',
        size: 'small',
        buttons: {
            unassign: {
                label: 'Remove from Slot',
                className: 'btn-default pull-left',
                callback: function () {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/artifacts/unassign/' + artifact_id + '/',
                        global: false
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
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/artifacts/delete/' + artifact_id + '/',
                        global: false,
                        data: {
                            "delete": "delete",
                            "artifact_id": artifact_id
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

function CopyMonster(instance_id) {
    $.get('/profile/' + PROFILE_NAME + '/monster/copy/' + instance_id + '/', function() {
        //DisplayMessages();
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
                        type: 'get',
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
            if(result.code === 'success') {
                UpdateAll();
            } else {
                bootbox.dialog({
                    title: 'Awaken Monster',
                    message: result.html
                });
                $('.rating').rating();
            }
        });
    }
}

function PowerUpMonster(instance_id) {
    if (instance_id) {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/monster/powerup/' + instance_id + '/'
        }).done(function(result) {
            bootbox.dialog({
                title: 'Power Up Monster',
                message: result.html
            });
        });
    }
}

// Page update functions
function UpdateRunes() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/runes/',
        type: 'get',
        global: false
    }).done(function(result) {
        $('#monster-view-runes').html(result);
        $('.popover').remove();
    });
}

function UpdateStats() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/stats/',
        type: 'get',
        global: false
    }).done(function(result) {
        $('#monster-view-stats').html(result);
    });
}

function UpdateSkills() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/skills/',
        type: 'get',
        global: false
    }).done(function(result) {
        $('#monster-view-skills').html(result);

        $('[data-bs-toggle="popover"]').popover({
            html:true
        });
    });
}

function UpdateNotes() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/view/' + INSTANCE_ID + '/info/',
        type: 'get',
        global: false
    }).done(function(result) {
        $('#monster-view-notes-info').html(result);
    });
}

function UpdateAll() {
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
    .on('click', '.rune-remove-all', function() { RemoveAllRunes($(this).data('instance-id'))})
    .on('click', '.artifact-edit', function() { EditArtifact($(this).data('artifact-id')) })
    .on('click', '.artifact-unassign', function() { UnassignArtifact($(this).data('artifact-id')) })
    .on('click', '.artifact-assign', function() { AssignArtifact($(this).data('artifact-slot')) })
    .on('click', '.artifact-assign-choice', function() { AssignArtifactChoice($(this).data('artifact-id'), $(this).data('instance-id')) })
    .on('click', '.monster-edit', function() { EditMonster($(this).data('instance-id')) })
    .on('click', '.monster-copy', function() { CopyMonster($(this).data('instance-id')) })
    .on('click', '.monster-delete', function() { DeleteMonster($(this).data('instance-id')) })
    .on('click', '.monster-awaken', function() { AwakenMonster($(this).data('instance-id')) })
    .on('click', '.monster-power-up', function() { PowerUpMonster($(this).data('instance-id')) })
    .on('click', '#addNewRune', function() { CreateNewRune($("#id_assign-slot_0").val()) })
    .on('click', '#addNewArtifact', function() { CreateNewArtifact($("#id_assign-slot").val()[0]) })
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
    .on('submit', '#AssignArtifactForm', function() {
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            if (data.code === 'results') {
                $('#assign_artifact_results').replaceWith(data.html)
            }
            else {
                alert('Unable to retrieve search results :(')
            }
        });

        return false;  //cancel default on submit action.
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
    .on('shown.bs.modal', function() {
        $("[data-provide='slider']").slider('relayout');
    })
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
        }).done(function (result) {
            if (result.code === 'success') {
                $('.modal.show').modal('hide');
                UpdateAll();

                if (result.removeElement) {
                    $(result.removeElement).remove();
                }
            }
            else if (result.code === 'edit') {
                $('.modal.show').modal('hide');
                UpdateAll();
                EditMonster(INSTANCE_ID);
            }
            else {
                $form.replaceWith(result.html);
                $('.rating').rating();
            }
        });

        return false;  //cancel default on submit action.
    });
