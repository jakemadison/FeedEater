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
function all_feeds(page) {
    $.post('/allfeeds').done(function() {

        //make all feeds look active
        $(".catbtn").removeClass('btn-default');
        $(".catbtn").removeClass('inactive-category');

        $(".catbtn").addClass('btn-success');
        $(".catbtn").addClass('active-category');

        //$(".catbtn").css("font-weight","Bold");


        recalculateEntries(page);




    }); //needs a fail function here...
}

//this should hide/show full category:
function toggleCategory(catname, page) {

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

        recalculateEntries(page);

    });

}

//show single feed
function oneFeedOnly(uf_id, page) {
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

        recalculateEntries(page);

    });

}


//turn a single feed on/off
function togglefeed(uf_id, page) {

    // sends post request to view.py

    console.log(page);

    $.post('/change_active', {
        uf_id: uf_id
    }).done(function() {

    $(".uf_id"+uf_id).toggleClass('btn-success');
    $(".uf_id"+uf_id).toggleClass('active-category inactive-category');

    recalculateEntries(page);
    });




}



function recalculateEntries(current_page, star_only) {

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
        active_list: active_list,
        star_only: star_only

    }).done(function(result) {

        console.log('successfully posted');
        console.log(result);
        console.log('+++++++');
        console.log(result.e);
        console.log('---');

        //replacing them is not going to work.
        //i need to erase all existing elements, and redraw completely

        $('.entry_container').empty()

        var entry_length = result.e.length;

        if (entry_length == 0) {

            $('.paging_div').remove();

            $('.entry_container').append('\
            <div class="col-md-8-2 no_entry_alert">\
                <div class="alert alert-info"><p align="center"><b>There are no entries to display.</b></p></div>\
            </div>\
            ');
        }
        else {
            $('.no_entry_alert').remove();

            //draw progress bar and update in loop below

            $('#pbar').width('10%');

            for (i=0; i<entry_length; i++) {
                console.log(result.e[i]);
                var amt = 10*(i+1);
                var per = amt+"%";

                $('#pbar').css("width: ","100%");

                console.log(per);
                console.log(amt+"%");
                console.log($('#pbar').width());
                drawEntries(result.e[i]);
            }

            console.log('done!');
            $('#pbar').width(0);
        }

    });
}


function drawEntries(entry){

    //console.log(entry);
    //console.log('-');

    var e_head = '\
        <div class="feedid'+entry.feed_id+' entry_list" entryId="'+entry.entry_id+'">\
        <div class="col-md-8-2" xmlns="http://www.w3.org/1999/html">\
    ';

    //set title information
    var e_title='\
       <h3>\
        <b><a  href="'+entry.entry_link+'" target="_blank"\
            data-toggle="tooltip" data-original-title="'+entry.entry_title+'"\
            class="'+entry.entry_title+'"\
            title="'+entry.entry_title+'">'+entry.entry_title+'</a></b>\
        </h3>\
        </div>\
    ';


    //check if we are compressed view or not
    if ($('.viewchange').hasClass('glyphicon-th-list')) {
        var e_view = '<div class="entrycontent compview">'
    }
    else {
        var e_view = '<div class="entrycontent fullview">'
    }

    var togs = "'#star"+entry.entry_id+"'"

    //check if our entry is starred or not
    if (entry.entry_starred === true) {

        var star = '<span class="glyphicon star glyphicon-star"\
         id="star' + entry.entry_id + '" \
         title="star: '+entry.entry_id+'" \
         onclick="startoggle('+togs+')"></span>'
    }
    else {

        var star = '<span class="glyphicon star glyphicon-star-empty"\
        id="star' + entry.entry_id + '" \
        title="star: '+entry.entry_id+'" \
        onclick="startoggle('+togs+')"></span>'
    }


//<span class="glyphicon star glyphicon-star-empty" id="star{{entry.id}}"
//                  title="star: {{entry.id}}" onclick="startoggle('#star{{entry.id}}')">
//            </span>





    var e_main = '\
        <div class="well">\
        <div class="row" id="info">\
        <span class="glyphicon glyphicon-info-sign" style="float:left"></span>\
        '+star+'\
        <p align="right"><span class="brand"><i>'+entry.url+'</i> @ '+entry.entry_published+'</span></p>\
        </span>\
        </div>\
        <p align="center">'+entry.entry_content+'</p>\
        </div>\
        </div>\
        </div>\
       ';

    $('.entry_container').append(e_head, e_view, e_title, e_main);


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

function addFeed(page) {
    console.log('beginning addFeeeeeeed');

    var submission = $("#add_feed_text").val();
    console.log(submission)
    $.post('/add_feed', {data:submission}).done(function(result) {

        console.log('hey! i actually finished!!');
        console.log(result);

        if (result.category == 'error') {

            $('#error_msg').show();
            $('#error_msg span').text(result.msg);
        }
        else {
            $('#info_msg').show();
            $('#info_msg span').text(result.msg);

            if (result.category == 'success') {
                recalculateEntries(page);
            }
        }

    });



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



