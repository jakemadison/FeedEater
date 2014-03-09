// left and right keys to move pages when appropriate, a la tumblr
// can expand this for other controls (star? tags even?)
$(document).keydown(function(event) {

    if ($(".input_thing").is(":focus")) {  // check if we are in an input thing and don't change page if so
        return;
    }

    var ch = event.keyCode || event.which;  //get keypress

    if (ch == 37){
        if ($(".previous").length !== 0){  // if we can go left, go left
            var h = $(".previous").children('a').attr('href');
            window.location = h;
        }
        event.preventDefault();

    }
    else if (ch == 39) {
        console.log('right');
        if ($(".next").length !== 0){  // if we can go right, go right
            var h = $(".next").children('a').attr('href');
            window.location = h;
        }
        event.preventDefault();
    }
});


//This is a stub for redrawing the sub list.  Basically, this should get called on changes to
//feeds, adding/deleting/changing categories, and should erase current sublist
//and create anew from an ajax call so we don't lose our current page.
function redrawSublist() {
    return;
}




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

    //this needs a post function somewhere...

    $(folderid).toggleClass('glyphicon-folder-open glyphicon-folder-close');
    $(catid).toggle();
}


//change a feed category:
function change_cat(catid, catnew, uf_id) {

    $.post('/changecat', {
        current_cat_name: catid,
        cat_new: catnew,
        uf_id: uf_id
        });

    // on success, this needs to rearrange the subscription list.. somehow...

}

//show all feeds
function all_feeds() {
    $.post('/allfeeds').done(function() {

        //make all feeds look active
        $(".catbtn").removeClass('btn-default');
        $(".catbtn").removeClass('inactive-category');

        $(".catbtn").addClass('btn-success');
        $(".catbtn").addClass('active-category');

        //$(".catbtn").css("font-weight","Bold");


    }); //needs a fail function here...
}

//this should hide/show full category:
function toggleCategory(catname) {

    $.post('/activatecategory', {
        catname: catname

    }).done(function() {

    //change active/deactivate state for these categories

    $(".catbtn").removeClass('btn-success');
    $(".catbtn").removeClass('active-category');
    $(".catbtn").addClass('inactive-category');
    $(".catbtn").addClass('btn');


    $("."+catname).addClass('btn-success');
    $("."+catname).removeClass('inactive-category');
    $("."+catname).addClass('active-category');


    });

}

//show single feed
function oneFeedOnly(uf_id) {
    $.post('/onefeedonly', {

        uf_id: uf_id

    }).done(function() {

    //change active states here.
    $(".catbtn").removeClass('btn-success');
    $(".catbtn").removeClass('active-category');
    $(".catbtn").addClass('inactive-category');
    $(".catbtn").addClass('btn');

    $(".uf_id"+uf_id).toggleClass('btn-success');
    $(".uf_id"+uf_id).toggleClass('active-category inactive-category');


    });

}


//turn a single feed on/off
function togglefeed(uf_id) {

    // sends post request to view.py
    $.post('/change_active', {
        uf_id: uf_id
    }).done(function() {

    $(".uf_id"+uf_id).toggleClass('btn-success');
    $(".uf_id"+uf_id).toggleClass('active-category inactive-category');

    });


    //recalculateEntries();

}


// there needs to be a "load/reload/update entries javascript function
// which other functions can call on to refresh actual content
// hmmmm...... to do this, we'll need to access the paging object and reset it.. hrrrmmm...
// OKAY, so hitting next page does re-run our pagination query, so our JS function here, just needs to
// recalculate query, using page as indexing (figure out what page we're on as offset), then return entries
// as json, then remove all current entries and put our jsonified ones up!


function recalculateEntries(current_page) {

    // first remove all entries that exist now
    // then put up loading sign
    // then get list, query DB, attempt to return entries
    // then get rid of loading sign (progress bar?)
    // then put up new entries


    //get list of currently active entries

    var active_list = [];

    $(".active-category").each(function() {
        var classList =$(this).attr('class').split(/\s+/);
        for (var i=0; i<classList.length; i++){
            if (classList[i].indexOf('uf_id') !== -1) {
                console.log(classList[i]);
                active_list.push(classList[i]);
            }
        }
    });

    console.log('FINAL!');
    console.log(active_list);

    $.post('/recalculate_entries', {
        current_page: current_page,
        active_list: active_list

    }).done(function(e) {

        console.log('successfully posted');
        console.log(e);
        console.log('---');

    });


    //send that to entries.py

    //return jsonified list of entries

    //recreate those entries on main page


}


function refreshFeeds() {

    //get a list of all feeds
    //draw a progress bar
    //iterate through them one by one, calling refresh
    //as soon as refresh is done, update progress bar by total/num_done*100
    //call recalc entries?
    //send next feed for updating...
    //etc, till done
    //remove progress bar


}

function addFeed() {
    console.log('beginning addFeeeeeeed');

    var submission = $("#add_feed_text").val();
    console.log(submission)
    $.post('/add_feed', {data:submission}).done(console.log('hey! i actually finished!!'));

    //this has to display errors and info
    //then it needs to recalculate subs list and entries

    return false;
}


function changeView() {
    console.log('beginning changeview');
    $.post('/change_view').done(function () {

        console.log('hey! i actually finished!!');
        $('.entrycontent').toggleClass('compview fullview');
        $('.viewchange').toggleClass('glyphicon-th-list glyphicon-align-justify');
            }
        );

}



