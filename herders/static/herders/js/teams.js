var team_detail = $('#team-detail');
var team_list = $('#team-list');
var page_content = $('div.content');

page_content.on('click', '.team-link', function() {
    var team_id = $(this).data('team-id');
    team_detail.load('/profile/' + PROFILE_NAME + '/teams/detail/' + team_id + '/');
});

page_content.on('click', '.team-edit', function() {
    var team_id = $(this).data('team-id');
    if (typeof team_id === 'undefined') {
        team_detail.load('/profile/' + PROFILE_NAME + '/teams/add/');
    }
    else {
        team_detail.load('/profile/' + PROFILE_NAME + '/teams/edit/' + team_id + '/');
    }
});

page_content.on('submit', '#EditTeamForm', function() {
    var frm = $('#EditTeamForm');
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
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

$(window).hashchange(load_new_team());
$(document).ready(function() {
    load_new_team();
    update_team_list();
});

function load_new_team() {
    var hashStr = location.hash.replace("#","");
    if (hashStr) {
        team_detail.load('/profile/' + PROFILE_NAME + '/teams/detail/' + hashStr + '/');
    }
    $('.autocomplete-light-widget').remove();
}

function update_team_list() {
    team_list.load('/profile/' + PROFILE_NAME + '/teams/list');
    $('.autocomplete-light-widget').remove();
}
