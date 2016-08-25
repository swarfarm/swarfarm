function EditBuilding($el) {
    var building_id = $el.data('building-id');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/buildings/edit/' + building_id.toString() + '/',
        global: false
    }).done(function(result) {
        bootbox.dialog({
            title: 'Edit Building',
            message: result.html
        });
    })
}

$('body')
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
                if (data.instance_id != 'undefined') {
                    // Try to find a matching monster container and replace it
                    var $building_row = $('.inventory-element[data-building-id="' + data.instance_id + '"]');

                    if ($building_row.length) {
                        // Replace it
                        $building_row.replaceWith(data.html);
                    }
                }
            }
            else {
                $form.replaceWith(data.html);
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.edit-building', function() { EditBuilding($(this))});