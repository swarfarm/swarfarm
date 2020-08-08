$(document).ready(function() {
    update_artifact_inventory();
});

function update_artifact_inventory() {
    $('#FilterInventoryForm').submit();
}

function update_slot_visibility() {
    const is_element = $('#id_slot').val() === "1";
    $('#div_id_element').toggleClass('hidden', !is_element);
    $('#div_id_archetype').toggleClass('hidden', is_element);
}

$('body')
    .on('click', '#FilterInventoryForm :submit', function() {
        var $form = $(this).closest('form');
        $('<input>').attr({
            type: 'hidden',
            id: 'id' + $(this).attr('name'),
            name: $(this).attr('name'),
            value: $(this).attr('value')
        }).appendTo($form);
    })
    .on('submit', '.ajax-form', function() {
        //Handle add ajax form submit
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),
            global: false
        }).done(function(result) {
            if (result.code === 'success') {
                $('.modal.in').modal('hide');
                update_artifact_inventory();

                if (result.removeElement) {
                    $(result.removeElement).remove();
                }
            }

            $form.replaceWith(result.html);
            $('[data-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });
            update_slot_visibility();
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.artifact-add', function() {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/artifacts/add/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Add artifact",
                size: "large",
                message: data.html
            });
        });
    })
    .on('click', '.artifact-edit', function() {
        //Pull in edit form on modal show
        var artifact_id = $(this).data('artifact-id');

        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/artifacts/edit/' + artifact_id + '/',
            global: false
        }).done(function(data) {
            bootbox.dialog({
                title: "Edit artifact",
                size: "large",
                message: data.html
            });
            update_slot_visibility();
        });
    })
    .on('click', '.artifact-delete', function() {
        //Pull in delete confirmation form on modal show
        var id = $(this).data('artifact-id');

        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function(result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/artifacts/delete/' + id + '/',
                        data: {
                            "delete": "delete",
                            "artifact_id": id
                        }
                    }).done(function () {
                        update_artifact_inventory();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    })
    .on('change', '#id_slot', function() {
        update_slot_visibility();
    })
    .on('submit', '#FilterInventoryForm', function() {
        ToggleLoading($('body'), true);

        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize()
        }).done(function (data) {
            ToggleLoading($('body'), false);
            $('#rune-inventory').replaceWith(data);
            $('#runeInventoryTable').tablesorter({
                widgets: ['saveSort', 'stickyHeaders'],
                widgetOptions: {
                    filter_reset: '.reset',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 50
                }
            });
            $('[data-toggle="tooltip"]').tooltip();
        });

        return false;  //cancel default on submit action.
    })
    .on('shown.bs.collapse', '#runeFilterCollapse', function() {
        $("[data-provide='slider']").slider('relayout');
    })
    .on('click', '.reset', function() {
        $('#runeInventoryTable').trigger('sortReset');
        var $form = $('#FilterInventoryForm');
        $form[0].reset();

        //Select2 inputs
        $form.find('select').each(function() {
            $(this).val(null).trigger("change");
        });

        //Sliders
        $form.find("[data-provide='slider']").each(function() {
            var $el = $(this),
                min = $el.data('slider-min'),
                max = $el.data('slider-max');
            $(this).slider('setValue', [min, max]);
        });

        update_artifact_inventory();
    })
    .on('click', '.box-group-mode', function() {
        var group_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/artifacts/inventory/box/' + group_mode + '/', function() {
            update_artifact_inventory();
        });
    });
