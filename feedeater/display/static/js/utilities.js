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


function startoggle(starid) {

    //change to loading, do DB call, then return success, change to star-full
    //on fail, change to fail icon.

    $.post('/star', {
        starid: starid
    });

    $(starid).toggleClass('glyphicon-star-empty glyphicon-star');

}


// toggles hiding/showing category:
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

//show all feeds
function all_feeds() {
    $.post('/allfeeds').done(function() {

        //make all feeds look active
        $(".catbtn").removeClass('btn-default');
        $(".catbtn").addClass('btn-success');
        $(".catbtn").css("font-weight","Bold");


    }); //needs a fail function here...
}

//this should hide/show full category:
function toggleCategory(catname) {

    $.post('/activatecategory', {
        catname: catname

    }).done(function() {

    //change active/deactivate state for these categories
    //these should really just change cat css "active" "inactive"... way simpler.
    $(".catbtn").removeClass('btn-success');
    $(".catbtn").addClass('inactive-category');
    $(".catbtn").addClass('btn');
    $(".catbtn").css("font-weight","Normal");

    $("."+catname).addClass('btn-success');
    $("."+catname).addClass('active-category');
    $("."+catname).css("font-weight","Bold");

    });

}


function togglefeed(uf_id) {

    // sends post request to view.py
    $.post('/change_active', {
        uf_id: uf_id
    }).done(function() {

    $(".uf_id"+uf_id).toggleClass('btn-success');
    $(".uf_id"+uf_id).toggleClass('active-category inactive-category');

    });

}


// there needs to be a "load/reload/update entries javascript function
// which other functions can call on to refresh actual content
// hmmmm...... to do this, we'll need to access the paging object and reset it.. hrrrmmm...