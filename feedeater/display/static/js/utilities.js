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


//what is this?
function subClick() {
    pageid = document.getElementById("url");
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

            var total_length = $('.catbtn').length;  //how many are there?
            var per_length = arraylength/total_length*100;  //percentage are done?
            var prog_length = per_length*0.9; //what is 90% of that value?
            var final_length = prog_length+10; //add the start length

            $('#pbar').width(final_length+'%');

        }

        if(!data.done) {
            setTimeout(function() {
                processProgress(p);
                }, 2000);
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



