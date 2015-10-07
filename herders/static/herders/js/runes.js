//Handle add ajax form submit
$('body').on('submit', '.ajax-form', function() {
    var $form = $(this);
    $.ajax({
        type: $form.attr('method'),
        url: $form.attr('action'),
        data: $form.serialize()
    }).done(function(data) {
        if (data.code === 'success') {
            $form.replaceWith(data.html);
            $('#addRuneModal').modal('hide');
            //TODO: Reload rune inventory.
        }
        else {
            $form.replaceWith(data.html);
        }


        $('.rating').rating();

    });

    return false;  //cancel default on submit action.
});