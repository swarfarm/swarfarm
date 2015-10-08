var rune_inventory = $('#rune-inventory');

$(document).ready(function() {
    update_rune_inventory();
});

function update_rune_inventory() {
    rune_inventory.load('/profile/' + PROFILE_NAME + '/runes/inventory');
}

//Handle add ajax form submit
$('body').on('submit', '.ajax-form', function() {
    var $form = $(this);
    $.ajax({
        type: $form.attr('method'),
        url: $form.attr('action'),
        data: $form.serialize()
    }).done(function(data) {
        if (data.code === 'success') {
            $('.modal.in').modal('hide');
            update_rune_inventory();
        }
        $form.replaceWith(data.html);
        $('.rating').rating();
    });

    return false;  //cancel default on submit action.
});