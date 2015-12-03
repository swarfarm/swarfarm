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
            var bestiary_table = $('#bestiary_table');
            bestiary_table.tablesorter({
                widgets: ['saveSort', 'columnSelector', 'stickyHeaders'],
                serverSideSorting: true,
                widgetOptions: {
                    filter_reset: '.reset',
                    columnSelector_container : '#column-selectors',
                    columnSelector_saveColumns: true,
                    columnSelector_mediaquery: false,
                    columnSelector_layout: '<label class="checkbox-inline"><input type="checkbox">{name}</label>',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 100
                }
            })
            .bind('sortBegin', function(e, table) {
                var sortColumn = e.target.config.sortList[0][0];
                var sortDirection = e.target.config.sortList[0][1] == 0 ? 'asc' : 'desc';
                var sort_header = slugify($(table).find('th')[sortColumn].innerText);

                $('#id_sort').val(sort_header + ';' + sortDirection);
                update_inventory();
            });

            // Trigger a sort reset if the sort form field is empty
            if (!$('#id_sort').val()) {
                bestiary_table.trigger('sortReset');
                bestiary_table.trigger('saveSortReset');
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.reset', function() {
        $('#monster_table').trigger('sortReset');
        var form = $('#FilterBestiaryForm');
        form[0].reset();
        $('#id_sort').val('');
        form.find('label').toggleClass('active', false);

        update_inventory();
    })
    .on('click', '.pager-btn', function() {
        $('#id_page').val($(this).data('page'));
        update_inventory();
    });