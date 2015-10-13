var rune_inventory = $('#rune-inventory');

$(document).ready(function() {
    update_rune_inventory();
});

function update_rune_inventory() {
    rune_inventory.load('/profile/' + PROFILE_NAME + '/runes/inventory');
}


$('body').on('submit', '.ajax-form', function() {
    //Handle add ajax form submit
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
        update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
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
}).on('change', '#edit_id_slot', function() {
    update_main_slot_options($('#edit_id_slot').val(), $('#edit_id_main_stat'));
}).on('change', '#id_slot', function() {
    update_main_slot_options($('#id_slot').val(), $('#id_main_stat'));
});

function update_main_slot_options(slot, main_stat_input) {
    $.ajax({
        type: 'get',
        url: API_URL + 'runes/stats_by_slot/' + slot.toString() + '/'
    }).done(function (response) {
        if (response.code === 'success') {
            // Record the current stat to see if we can pick it in the new list
            var current_stat = main_stat_input.val();

            main_stat_input.empty();
            $.each(response.data, function (val, text) {
                main_stat_input.append(
                    $('<option></option>').val(val).html(text)
                );
            });

            var exists = 0 != main_stat_input.find('option[value='+current_stat+']').length;
            if (exists) {
                main_stat_input.val(current_stat);
            }
            else {
                for(var key in response.data) break;
                main_stat_input.val(key);
            }
        }
    });
}
