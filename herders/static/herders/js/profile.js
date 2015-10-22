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
                        location.reload();
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
                location.reload();
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
    .on('click', '.monster-delete', function() { DeleteMonster($(this).data('instance-id')) });