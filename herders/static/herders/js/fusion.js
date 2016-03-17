function EssenceStorage() {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/storage/'
    }).done(function(result) {
        bootbox.dialog({
            title: 'Essence Inventory',
            size: 'large',
            message: result.html
        });
    })
}

$('body')
    .on('click', '.essence-storage', function() { EssenceStorage() })
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
            }
            else {
                alert('Error saving essences :(');
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('shown.bs.tab', function (e) {
        var fusion = $(e.target).data('fusion');
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/fusion/' + fusion + '/'
        }).done(function(data) {
            $('#'+fusion).html(data);
        });
    });