//Initialize all bootstrap tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});


//Modal management scripts
var addMonsterModal = $('#addMonsterModal');

addMonsterModal.on('shown.bs.modal', function () {
    $('#id_monster-autocomplete').focus()
});
