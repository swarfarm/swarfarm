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
}).on('show.bs.modal', '#editRuneModal', function(event) {
    //Pull in edit form on modal show
    var rune_id = $(event.relatedTarget).data('rune-id');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/edit/' + rune_id + '/'
    }).done(function(data) {
        $('#editRuneForm').empty().append(data.html);
        $('.rating').rating();
    });
}).on('show.bs.modal', '#deleteRuneModal', function(event) {
    //Pull in delete confirmation form on modal show
    var rune_id = $(event.relatedTarget).data('rune-id');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/runes/delete/' + rune_id + '/'
    }).done(function(data) {
        $('#deleteRuneConfirmation').empty().append(data.html);
    });
});
