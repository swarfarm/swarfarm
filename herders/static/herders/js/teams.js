var team_detail = $('#team-detail');
var team_list = $('#team-list');
var page_content = $('#wrap');

$('body').on('submit', '.ajax-form', function() {
    //Handle add ajax form submit
    var $form = $(this);
    $.ajax({
        type: $form.attr('method'),
        url: $form.attr('action'),
        data: $form.serialize()
    }).done(function(result) {
        $('.modal.in').modal('hide');
    });

    return false;  //cancel default on submit action.
});

page_content.on('click', '.team-link', function() {
    var team_id = $(this).data('team-id');
    team_detail.load('/profile/' + PROFILE_NAME + '/teams/detail/' + team_id + '/', function() {
        $('[data-toggle="popover"]').popover();
    });
});

page_content.on('click', '.team-edit', function() {
    var team_id = $(this).data('team-id');
    if (typeof team_id === 'undefined') {
        team_detail.load('/profile/' + PROFILE_NAME + '/teams/add/', function() {
            initSelect();
        });
    }
    else {
        team_detail.load('/profile/' + PROFILE_NAME + '/teams/edit/' + team_id + '/', function() {
            initSelect();
        });
    }
});

page_content.on('submit', '#EditTeamForm', function() {
    var frm = $('#EditTeamForm');
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        global: false,
        success: function (data) {
            team_detail.html(data);
            update_team_list();
        },
        error: function () {
            alert("Sorry, something didn't work.");
        }
    });
    return false;
});

$(document).ready(function() {
    update_team_list();
    load_new_team();
});

function load_new_team() {
    var hashStr = location.hash.replace("#","");
    if (hashStr) {
        team_detail.load('/profile/' + PROFILE_NAME + '/teams/detail/' + hashStr + '/', function() {
            $('[data-toggle="popover"]').popover();
        });
    }
    $('[data-input-id="id_leader-autocomplete"]').remove();
    $('[data-input-id="id_roster-autocomplete"]').remove();
    DisplayMessages();
}

function update_team_list() {
    team_list.load('/profile/' + PROFILE_NAME + '/teams/list', function() {
        var isEmpty = team_list.children('p:contains("Group list is empty!")').length > 0;
        $('.navbar .team-edit').toggleClass('disabled', isEmpty);
    });
    $('[data-input-id="id_leader-autocomplete"]').remove();
    $('[data-input-id="id_roster-autocomplete"]').remove();
}
