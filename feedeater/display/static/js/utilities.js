function subClick() {
    pageid = document.getElementById("url");
}


function set_openid_new(openid, pr) {
    u = openid.search('<username>')
    if (u != -1) {
        // openid requires username
        user = prompt('Enter your ' + pr + ' username:')
        openid = openid.substr(0, u) + user
    }
    form = document.forms['login_form'];
    form.elements['openid'].value = openid
}

function tag(tagtext, tagid) {
    // sends post request to view.py
    $.post('/tags', {
        tagtext: tagtext,
        tagid: tagid

    //this runs after function in view.py is done
    });
}


function togglefeed(uf_id) {

    $(uf_id).hide();
    // sends post request to view.py
    $.post('/togglefeed', {
        ufid: uf_id
    });

}


function startoggle(starid) {

    //change to loading, do DB call, then return success, change to star-full
    //on fail, change to fail icon.

    $.post('/star', {
        starid: starid
    });

    $(starid).toggleClass('glyphicon-star-empty glyphicon-star');

}

function foldertoggle(folderid, catid) {

    $(folderid).toggleClass('glyphicon-folder-open glyphicon-folder-close');
    $(catid).toggle();
}




function change_cat(catid, catnew, uf_id) {

    $.post('/changecat', {
        current_cat_name: catid,
        cat_new: catnew,
        uf_id: uf_id
        });

}

