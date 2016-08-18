// Check for hash pointing at specific fusion product
var url = document.location.toString();
var selected_fusion;

function updateFusion() {
    ToggleLoading($('.navmenu-content'), true);
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/fusion/' + selected_fusion + '/'
    }).done(function(data) {
        $('#fusion').html(data);
        ToggleLoading($('.navmenu-content'), false);
        document.location.hash = "#" + selected_fusion;
    });
}

$(document).ready(function() {
    if (document.location.hash) {
        selected_fusion = document.location.hash.replace('#', '');
    }
    else {
        // Load the first one
        selected_fusion = $('.fusion-tab').first().data('fusion');
    }

    updateFusion();
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
        selected_fusion = $(this).data('fusion');
        updateFusion();
    });
