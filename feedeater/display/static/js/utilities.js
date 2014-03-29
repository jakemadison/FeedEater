// left and right keys to move pages when appropriate, a la tumblr
// can expand this for other controls (star? tags even?)
$(document).keydown(function(event) {

    if ($(".input_thing").is(":focus")) {  // check if we are in an input thing and don't change page if so
        return;
    }

    var ch = event.keyCode || event.which;  //get keypress

    if (ch == 37){

        var $prev = $(".previous");

        if ($prev.length !== 0){  // if we can go left, go left
            var h = $prev.children('a').attr('href');
            window.location = h;
        }
        event.preventDefault();

    }
    else if (ch == 39) {

        var $next = $(".next");

        if ($next.length !== 0){  // if we can go right, go right
            var h = $next.children('a').attr('href');
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

//what is this?
function subClick() {
    pageid = document.getElementById("url");
}

//
function set_openid_new(openid, pr) {
    var u = openid.search('<username>')
    if (u != -1) {
        // openid requires username
        var user = prompt('Enter your ' + pr + ' username:')
        openid = openid.substr(0, u) + user
    }
    var form = document.forms['login_form'];
    form.elements['openid'].value = openid
}

//
function tag(tagtext, tagid) {
    // sends post request to view.py
    $.post('/tags', {
        tagtext: tagtext,
        tagid: tagid

    //this runs after function in view.py is done
    });
}

//change the star state of an entry
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

        var $catbtn = $(".catbtn");

        //make all feeds look active
        $catbtn.removeClass('btn-default');
        $catbtn.removeClass('inactive-category');

        $catbtn.addClass('btn-success');
        $catbtn.addClass('active-category');

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

        var $catbtn = $(".catbtn");

        $catbtn.removeClass('btn-success');
        $catbtn.removeClass('active-category');
        $catbtn.addClass('inactive-category');
        $catbtn.addClass('btn');

        var $catname = $("."+catname);

        $catname.addClass('btn-success');
        $catname.removeClass('inactive-category');
        $catname.addClass('active-category');

        recalculateEntries(page);

    });

}

//show single feed
function oneFeedOnly(uf_id, page) {
    $.post('/onefeedonly', {

        uf_id: uf_id

    }).done(function() {

        //change active states here.
        var $catbtn = $(".catbtn");

        $catbtn.removeClass('btn-success');
        $catbtn.removeClass('active-category');
        $catbtn.addClass('inactive-category');
        $catbtn.addClass('btn');

        var $uf_sel = $(".uf_id"+uf_id);

        $uf_sel.toggleClass('btn-success');
        $uf_sel.toggleClass('active-category inactive-category');

        recalculateEntries(page);

    });

}

//turn a single feed on/off
function togglefeed(uf_id, page) {

    $.post('/change_active', {
        uf_id: uf_id
    }).done(function() {

        var $uf_sel = $(".uf_id"+uf_id);
        $uf_sel.toggleClass('btn-success');
        $uf_sel.toggleClass('active-category inactive-category');

        recalculateEntries(page);
    });

}

//recalculate which entries should be displayed
function recalculateEntries(current_page, star_only) {

    //get list of currently active entries
    var active_list = [];

    $(".active-category").each(function() {
        var classList =$(this).attr('class').split(/\s+/);
        for (var i=0; i<classList.length; i++){
            if (classList[i].indexOf('uf_id') !== -1) {
                active_list.push(classList[i]);
            }
        }
    });

    //now post to framework:
    $.post('/recalculate_entries', {
        current_page: current_page,
        active_list: active_list,
        star_only: star_only

    }).done(function(result) {

        console.log(result.e);

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

            for (var i=0; i<entry_length; i++) {
                drawEntries(result.e[i]);
            }
            console.log('done!');
        }
    });
}

//actually draws out entries. This needs work:
function drawEntries(entry){

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

//refresh all feeds:
function refreshFeeds(p) {

    $('.unreadcount').text('?');

    $('.refspan').toggleClass('glyphicon-refresh glyphicon-dashboard');
    $('#refbtn').disabled = true;


    $.post('/refreshfeeds').done(function() {

        console.log("finished refreshing feeds. Recalcing entries now");
        console.log("done!");
        $('.refspan').toggleClass('glyphicon-refresh glyphicon-dashboard');
        $('#refbtn').disabled = false;
    });

    console.log("done posting! carry on....");

    setTimeout(function() {
                    processProgress(p);
                }, 500);

}

//used for updating the progress bar.  this needs a timeout or it will just keep recursiveing
function processProgress(p){
    //recursive call to get progress and update
    console.log("processProgress is running now...");

    $.getJSON($SCRIPT_ROOT + '/get_progress',

        function(data) {
        console.log("inside get progress call...");
        console.log(data);
        console.log(data.fin.length);
        var arraylength = data.fin.length;

        for (var i=0; i < arraylength; i++) {

            //instead of redrawing everytime, let's just do that for new ones
            var $current_data = $('.f_id'+data.fin[i]);

            if (!$current_data.hasClass('btn-info')) {
                $current_data.removeClass('btn-success');
                $current_data.addClass('btn-info');
                getUnreadCount(data.fin[i]);
            }

            var total_length = $('.catbtn').length;
            var per_length = arraylength/total_length*100;

            $('#pbar').width(per_length+'%');
        }

        if(!data.done) {
            setTimeout(function() {
                processProgress(p);
                }, 500);
        }

        else {
            setTimeout(function() {

                var $cat_btn = $('.catbtn');
                $cat_btn.removeClass('btn-info');
                $cat_btn.addClass('btn-success');

                var $p_bar = $('#pbar');
                $p_bar.hide();
                $p_bar.width('0%');
                $p_bar.show();

            }, 1000);
        }

    }).done(function(data) {
            console.log("process progress has finished");
            recalculateEntries(p)
    });
}

//return the unread count for a feed (currently just the count):
function getUnreadCount(feed) {

    $.getJSON($SCRIPT_ROOT + '/get_unread_count', {
        'feed': feed

    }, function(data) {
        $('.f_id'+feed+' span').text(data.count);
    });
}

//add a new feed subscrition.  this needs to hook into processProgress function
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

//squishing/expanding entry contents:
function changeView() {
    console.log('beginning changeview');
    $.post('/change_view').done(function () {
            console.log('hey! i actually finished!!');
            $('.entrycontent').toggleClass('compview fullview');
            $('.viewchange').toggleClass('glyphicon-th-list glyphicon-align-justify');
       }
    );
}



