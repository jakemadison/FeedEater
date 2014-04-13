/**
 * Created by jmadison on 4/13/14.
 */


//This is a stub for redrawing the sub list.  Basically, this should get called on changes to
//feeds, adding/deleting/changing categories, and should erase current sublist
//and create anew from an ajax call so we don't lose our current page.
function redrawSublist() {
    return;
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


//refresh all feeds:
function refreshFeeds(p) {

    $('#pbar').width('10%'); //indicates we have started the request, since there is significant delay
                             //on the first request.  process progress needs to account for this.

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

        //make info text dissapear after 3 seconds.
        setTimeout(function() {
                    $('#info_msg span').hide();
                }, 3000);

    });
    //this has to display errors and info
    //then it needs to recalculate subs list and entries
    return false;
}























