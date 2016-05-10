// Check for hash pointing at specific fusion product
var url = document.location.toString();
if (url.match('#')) {
    $('.nav-pills a[href="#' + url.split('#')[1] + '"]').tab('show');
}

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

function updateFusion() {
    // Get the active tab
    var fusion = $(".fusion-tabs li.active>a").data('fusion');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/fusion/' + fusion + '/'
    }).done(function(data) {
        $('#'+fusion).html(data);
    });
}

$(document).ready(function() {
    updateFusion();
});

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
                updateFusion();
            }
            else {
                alert('Error saving essences :(');
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('shown.bs.tab', function (e) {
        updateFusion();
    });