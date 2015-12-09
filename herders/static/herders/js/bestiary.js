$(document).ready(function() {
    update_inventory();
});

function update_inventory() {
    $('#FilterBestiaryForm').submit();
}

function AddMonster(monster_pk, stars) {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/add/?monster=' + monster_pk.toString() + '&stars=' + stars.toString(),
        type: 'get'
    }).done( function(result) {
        bootbox.dialog({
            title: "Add Monster",
            message: result.html
        });
        $('.rating').rating();
    })
}


$('body')
    .on('click', '.monster-add', function() { AddMonster($(this).data('monster'), $(this).data('stars')) })
    .on('submit', '#FilterBestiaryForm', function() {
        ToggleLoading($('body'), true);

        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            ToggleLoading($('body'), false);
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
                var sortDirection = e.target.config.sortList[0][1] == 0 ? 'desc' : 'asc';
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
    })
    .on('submit', '.ajax-form', function() {
        //Handle add ajax form submit
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function(data) {
            if (data.code === 'success') {
                $('.modal.in').modal('hide');
            }
            else {
                $form.replaceWith(data.html);
                $('.rating').rating();
            }
        });

        return false;  //cancel default on submit action.
    });