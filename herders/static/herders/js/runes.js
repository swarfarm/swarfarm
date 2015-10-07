//Handle add rune form submit
var addRuneForm = $('#addRuneForm');
addRuneForm.on('submit', function() {
    $.ajax({
            type: addRuneForm.method,
            url: addRuneForm.action,
            data: addRuneForm.serialize(),
            success: function(data) {
                addRuneForm.replaceWith(data);
            }
    });

    return false;  //cancel default on submit action.
});