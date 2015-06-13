//Initialize all bootstrap tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});


//Modal management scripts
$('#addMonsterModal').on('shown.bs.modal', function () {
    $('#id_monster-autocomplete').focus()
});

//Select the
$('#id_monster-autocomplete').bind('selectChoice',
    function(e, choice, autocomplete) {
        alert('You selected: ' + choice.dataset['value']);
        //$('#id_stars'')
    }
);