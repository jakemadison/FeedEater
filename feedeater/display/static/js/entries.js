/**
 * Created by jmadison on 4/13/14.
 */


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

    var e_tags='<div class="tags"><a href="#"><span class="label label-default entry_cat_label" id="test1">\
            '+entry.category+'</span></a></div>';


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

    $('.entry_container').append(e_head, e_view, e_title, e_tags, e_main);


}



