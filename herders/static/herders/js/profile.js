var quickFodderAdded = false;

$(document).ready(function() {
    update_monster_form_with_query();
    update_monster_inventory();
});

function update_monster_form_with_query(){
    var params = new URLSearchParams(location.search)

    update_form_text_from_query(params, 'monster__name');

    update_form_multislider_from_query(params, 'stars');
    update_form_multislider_from_query(params, 'monster__natural_stars');
    update_form_multislider_from_query(params, 'level');
    update_form_multislider_from_query(params, 'monster__skills__cooltime');
    update_form_multislider_from_query(params, 'monster__skills__hits');

    update_form_multiselect_from_query(params, 'tags__pk');
    update_form_multiselect_from_query(params, 'priority');
    update_form_multiselect_from_query(params, 'monster__archetype');
    update_form_multiselect_from_query(params, 'monster__element');
    update_form_multiselect_from_query(params, 'monster__awaken_level');
    update_form_multiselect_from_query(params, 'buff_debuff_effects');
    update_form_multiselect_from_query(params, 'other_effects');
    update_form_multiselect_from_query(params, 'monster__skills__scaling_stats__pk');
    update_form_multiselect_from_query(params, 'monster__leader_skill__attribute');
    update_form_multiselect_from_query(params, 'monster__leader_skill__area');

    update_form_select_from_query(params, 'monster__skills__passive');
    update_form_select_from_query(params, 'monster__skills__aoe');

    update_form_radio_from_query(params, 'fodder');
    update_form_radio_from_query(params, 'in_storage');
    update_form_radio_from_query(params, 'monster__fusion_food');

    update_form_toggle_from_query(params, 'effects_logic');
}

function clean_monster_url_data(data){
    var cleanedParams = clean_query_params(data)
    var params = new URLSearchParams(cleanedParams)
    var multiSliderParams = ['stars', 'monster__natural_stars', 'level', 'monster__skills__cooltime', 'monster__skills__hits']
    var newData = clean_multi_slider_min_max_params(params, multiSliderParams)
    return newData
}

function update_monster_inventory() {
    $('#FilterInventoryForm').submit();
}

function AddMonster() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/add/',
        type: 'get'
    }).done( function(result) {
        bootbox.dialog({
            title: "Add Monster",
            message: result.html
        }).on('shown.bs.modal', function() {
            $(this).attr('id', 'addMonsterModal');
        });
        $('.rating').rating();
    })
}

function EditMonster(instance_id) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/edit/' + instance_id + '/'
    }).done(function(result) {
        bootbox.dialog({
            title: 'Edit Monster',
            message: result.html
        });
        $('.rating').rating();
    });
}

function CopyMonster(instance_id) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/copy/' + instance_id + '/'
    }).done(function(result) {
        $('.inventory-element[data-instance-id="' + instance_id + '"]').after(result.html);
        //update_monster_inventory();
    });
}

function AwakenMonster(instance_id) {
    if (instance_id) {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/monster/awaken/' + instance_id + '/'
        }).done(function(result) {
            if(result.code === 'success') {
                update_monster_inventory();
            } else {
                bootbox.dialog({
                    title: 'Awaken Monster',
                    message: result.html
                });
                $('.rating').rating();
            }
        });
    }
}

function DeleteMonster(instance_id) {
    if (instance_id) {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function (result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/monster/delete/' + instance_id + '/',
                    }).done(function () {
                        $(".inventory-element[data-instance-id='" + instance_id + "']").remove();
                        if ($('#monster_table').length) {
                            $('#monster_table').trigger('update');
                        }
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    }
    else {
        alert("Unspecified monster to delete");
    }
}

function AddMonsterPiece() {
    $.ajax({
        url: '/profile/' + PROFILE_NAME + '/monster/piece/add/',
        type: 'get'
    }).done( function(result) {
        bootbox.dialog({
            title: "Add Pieces",
            message: result.html
        });
    })
}

function EditMonsterPiece(instance_id) {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/piece/edit/' + instance_id + '/'
    }).done(function(result) {
        bootbox.dialog({
            title: 'Edit Pieces',
            message: result.html
        });
    });
}

function DeleteMonsterPiece(instance_id) {
    if (instance_id) {
        bootbox.confirm({
            size: 'small',
            message: 'Are you sure?',
            callback: function (result) {
                if (result) {
                    $.ajax({
                        type: 'get',
                        url: '/profile/' + PROFILE_NAME + '/monster/piece/delete/' + instance_id + '/'
                    }).done(function () {
                        $(".inventory-element[data-instance-id='" + instance_id + "']").remove();
                    }).fail(function () {
                        alert("Something went wrong! Server admin has been notified.");
                    });
                }
            }
        });
    }
    else {
        alert("Unspecified piece to delete");
    }
}

function SummonMonsterPiece(instance_id) {
    if (instance_id) {
        $.ajax({
            type: 'get',
            url: '/profile/' + PROFILE_NAME + '/monster/piece/summon/' + instance_id + '/'
        }).done(function (result) {
            $(".inventory-element[data-instance-id='" + instance_id + "']").replaceWith(result.html);
        }).fail(function () {
            alert("Something went wrong! Server admin has been notified.");
        });
    }
    else {
        alert("Unspecified piece to delete");
    }
}

function QuickFodderMenu() {
    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/quick_fodder/'
    }).done(function(result) {
        bootbox.dialog({
            title: 'Quick Fodder Menu',
            message: result.html
        }).on('hide.bs.modal', function() {
            if (quickFodderAdded) {
                update_monster_inventory();
                quickFodderAdded = false;
            }
        });
    })
}

function QuickFodder(btn) {
    var monster_id = btn.data('monster-id');
    var stars = btn.data('stars');
    var level = btn.data('level');

    $.ajax({
        type: 'get',
        url: '/profile/' + PROFILE_NAME + '/monster/quick_add/' + monster_id.toString() + '/' + stars.toString() + '/' + level.toString() + '/'
    });
}

function pickHex(left, max) {
    var rgbColor1 = [118, 255, 86];
    var rgbColor2 = [255, 226, 128];
    var rgbColor3 = [255, 114, 114];

    var color1 = rgbColor1;
    var color2 = rgbColor2;
    var fade = parseInt(left) / parseInt(max);

    // Do we have 3 colors for the gradient? Need to adjust the params.
    if (rgbColor3) {
      fade = fade * 2;

      // Find which interval to use and adjust the fade percentage
      if (fade >= 1) {
        fade -= 1;
        color1 = rgbColor2;
        color2 = rgbColor3;
      }
    }

    var diffRed = color2[0] - color1[0];
    var diffGreen = color2[1] - color1[1];
    var diffBlue = color2[2] - color1[2];

    var gradient = {
      red: parseInt(Math.floor(color1[0] + (diffRed * fade)), 10),
      green: parseInt(Math.floor(color1[1] + (diffGreen * fade)), 10),
      blue: parseInt(Math.floor(color1[2] + (diffBlue * fade)), 10),
    };

    return 'rgb(' + gradient.red + ',' + gradient.green + ',' + gradient.blue + ')';
}

$('body')
    .on('click', ':submit', function() {
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
            data: $form.serialize()
        }).done(function(data) {
            if (data.code === 'success') {
                $('.modal.show').modal('hide');
                if (data.instance_id != 'undefined') {
                    // Try to find a matching monster container and replace it
                    var $monster_container = $('.inventory-element[data-instance-id="' + data.instance_id + '"]');

                    if ($monster_container.length) {
                        // Replace it
                        $monster_container.replaceWith(data.html);
                        $('#monster_table').trigger('update', [true]);
                    }
                    else {
                        // Append it if we can in list mode. Box/pieces require server side grouping so just request it again.
                        var $inventory_container = $('#inventory-container');
                        if ($inventory_container.length) {
                            var $new_row = $(data.html);
                            $inventory_container.append($new_row);
                            $('#monster_table').trigger('addRows', [$new_row, true]);
                        }
                        else {
                            // This is also the default action for form submit
                            update_monster_inventory();
                        }
                    }
                }
                else {
                    update_monster_inventory();
                }
            }
            else {
                $form.replaceWith(data.html);
                $('.rating').rating();
            }
        });

        return false;  //cancel default on submit action.
    })
    .on('click', '.monster-add', function() { AddMonster() })
    .on('click', '.monster-edit', function() { EditMonster($(this).data('instance-id')) })
    .on('click', '.monster-copy', function() { CopyMonster($(this).data('instance-id')) })
    .on('click', '.monster-delete', function() { DeleteMonster($(this).data('instance-id')) })
    .on('click', '.monster-awaken', function() { AwakenMonster($(this).data('instance-id')) })
    .on('click', '.monster-piece-add', function() { AddMonsterPiece() })
    .on('click', '.monster-piece-edit', function() { EditMonsterPiece($(this).data('instance-id')) })
    .on('click', '.monster-piece-delete', function() { DeleteMonsterPiece($(this).data('instance-id')) })
    .on('click', '.monster-piece-summon', function() { SummonMonsterPiece($(this).data('instance-id')) })
    .on('click', '.quick-fodder-menu', function() { QuickFodderMenu() })
    .on('click', '.quick-fodder', function() {
        quickFodderAdded = true;
        QuickFodder($(this))
    })
    .on('click', '.profile-view-mode', function() {
        var view_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/monster/inventory/' + view_mode + '/', function() {
            update_monster_inventory();
        });
    })
    .on('click', '.box-group-mode', function() {
        var group_mode = $(this).data('mode');
        $.get('/profile/' + PROFILE_NAME + '/monster/inventory/box/' + group_mode + '/', function() {
            update_monster_inventory();
        });
    })
    .on('submit', '#FilterInventoryForm', function() {
        ToggleLoading($('body'), true);

        var $form = $(this);
        var formData = clean_monster_url_data($form.serialize())
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: formData
        }).done(function (data) {
            history.replaceState({}, "", this.url.substring(0, this.url.indexOf('/monster/inventory/')) + '/?' + formData)

            ToggleLoading($('body'), false);
            $('#monster-inventory').replaceWith(data);

            //Reinit everything
            $('[data-bs-toggle="tooltip"]').tooltip({
                container: 'body'
            });
            $('[data-bs-toggle="popover"]').popover({
                html:true,
                viewport: {selector: 'body', padding: 2}
            });

            $('#monster_table').tablesorter({
                sortList: [[2,1],[3,1]],
                sortReset: true,
                widgets: ['saveSort', 'columnSelector', 'stickyHeaders'],
                widgetOptions: {
                    filter_reset: '.reset',
                    columnSelector_container : '#column-selectors',
                    columnSelector_saveColumns: true,
                    columnSelector_mediaquery: false,
                    columnSelector_layout: '<div class="form-check me-3"><label class="form-check-label"><input class="form-check-input" type="checkbox">{name}</label></div>',
                    stickyHeaders_zIndex : 2,
                    stickyHeaders_offset: 50
                },
                theme: 'bootstrap',
            });

            $('td[id^="monster-collection-cell"]').each(function() {
                let background_color =  pickHex($(this).attr('data-left'), $(this).attr('data-max'))
                $(this).css('background-color', background_color)
            })
        });

        return false;  //cancel default on submit action.
    })
    .on('shown.bs.collapse', '#monsterFilterCollapse', function() {
        $("[data-provide='slider']").slider('relayout');
    })
    .on('click', '.reset', function() {
        $('#monster_table').trigger('sortReset');
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

        // Toggle button
        $("input[name='effects_logic']").prop("checked", false);
        $("input[name='effects_logic']").parent().addClass('off');
        
        update_monster_inventory();
    });
