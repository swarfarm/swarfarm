function update_form_text_from_query(params, element_id){
    if(params.has(element_id)) $("input[name='" + element_id + "']").val(params.get(element_id));
}

function update_form_multiselect_from_query(params, element_id){
    if(params.has(element_id)) $("select[name='" + element_id + "']").val(params.getAll(element_id));
}

function update_form_select_from_query(params, element_id){
    if(params.has(element_id)) $("select[name='" + element_id + "']").val(params.get(element_id));
}

function update_form_radio_from_query(params, element_id){
    if(params.has(element_id)) $("input[name='" + element_id + "']:radio[value='" + params.get(element_id) + "']").prop("checked", true);
}

function update_form_toggle_from_query(params, element_id){
    if(params.has(element_id)){
        $("input[name='" + element_id + "']").prop("checked", true);
        $("input[name='" + element_id + "']").parent().removeClass('off');
    }
    else {
        $("input[name='" + element_id + "']").prop("checked", false);
        $("input[name='" + element_id + "']").parent().addClass('off');
    };
}

function update_form_multislider_from_query(params, element_id){
    if(params.has(element_id)){
        var new_val = params.get(element_id).split(',');
        new_val = [parseInt(new_val[0]), parseInt(new_val[1])]
        $("input[name='" + element_id + "']").slider('setValue', new_val)
    }    
}

function clean_query_params(part_url){
    let new_url = part_url
    let clean = false;
    // 'While' loop because if there are few empty params next to eachother
    // URLSearchParams doesn't read them all correctly (skips every 2nd param)
    while(!clean){
        var params = new URLSearchParams(new_url)
        clean = true;
        for (let p of params) {
            if (p[1] === ""){
                params.delete(p[0]);
                clean = false;
            }
        }
        new_url = params.toString()
    }
    
    if(params.has('apply')) params.delete('apply');

    return params.toString()
}