


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
    .on('click', '.essence-storage', function() { EssenceStorage() });