$(document).ready(function() {
    update_inventory();
});

function update_inventory() {
    $('#FilterBestiaryForm').submit();
}


$('body')
    .on('submit', '#FilterBestiaryForm', function() {
        ToggleLoading($('#wrap'));

        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            ToggleLoading($('#wrap'), false);
            $('#bestiary-inventory').replaceWith(data);

            //Reinit everything
            $('[data-toggle="tooltip"]').tooltip({
                container: 'body'
            });
            $('[data-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });

            $('#bestiary_table').tablesorter({
                widgets: ['saveSort', 'columnSelector', 'stickyHeaders'],
                widgetOptions: {
                    filter_reset: '.reset',
                    columnSelector_container : '#column-selectors',
                    columnSelector_saveColumns: true,
                    columnSelector_mediaquery: false,
                    columnSelector_layout: '<label class="checkbox-inline"><input type="checkbox">{name}</label>',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 100
                }
            });
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.reset', function() {
        $('#monster_table').trigger('sortReset');
        $('#FilterBestiaryForm')[0].reset();
        update_inventory();
    });