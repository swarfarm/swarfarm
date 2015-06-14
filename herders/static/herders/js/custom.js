var api_url = 'http://swarfarm.com/api/';

//Initialize all bootstrap tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});


//Modal management scripts
$('#addMonsterModal').on('shown.bs.modal', function () {
    $('#id_monster-autocomplete').focus()
});

//Set the star rating upon selecting a monster from autocomplete
$('#id_monster-autocomplete').bind('selectChoice',
    function(e, choice, autocomplete) {
        var monster_id = choice[0].dataset['value'];

        $.getJSON(api_url + 'bestiary/' + monster_id, function(result){
            $('#id_stars').rating('rate', result[0].fields['base_stars']);
        });
    });