$(document).ready(function() {
    update_building_inventory();
});

function update_building_inventory() {
    ToggleLoading($('body'), true);
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/buildings/inventory/'
    }).done(function (result) {
        $('#buildings').html(result);
        ToggleLoading($('body'), false);
        $('[data-toggle="popover"]').popover({
            html:true,
            viewport: {selector: 'body', padding: 2}
        });
    })
}

function EditBuilding($el) {
    var building_id = $el.data('building-id');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/buildings/edit/' + building_id.toString() + '/',
        global: false
    }).done(function(result) {
        bootbox.dialog({
            title: 'Edit Building',
            className: 'edit-building-dialog',
            message: result.html
        });
    })
}

$('body')
    .on('shown.bs.modal', '.edit-building-dialog', function() {
        $('#id_level').select();
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
                update_building_inventory();
            }
            else {
                $form.replaceWith(data.html);
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.edit-building', function() { EditBuilding($(this))});