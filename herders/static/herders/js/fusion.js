// Check for hash pointing at specific fusion product
var url = document.location.toString();
if (url.match('#')) {
    $('.nav-pills a[href="#' + url.split('#')[1] + '"]').tab('show');
}

function updateFusion(fusion) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/fusion/' + fusion + '/'
    }).done(function(data) {
        $('#fusion').html(data);
    });
}

$(document).ready(function() {
    // Find the first fusion link and load it
    var fusion = $('.fusion-tab').first().data('fusion');
    updateFusion(fusion);
});

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
                updateFusion();
            }
            else {
                alert('Error saving essences :(');
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.fusion-tab', function () {
        var fusion = $(this).data('fusion');
        updateFusion(fusion);
    });