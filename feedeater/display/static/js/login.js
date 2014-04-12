/**
 * Created by jmadison on 4/12/14.
 */


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


function start_login() {

    console.log('starting login');

    var x = document.getElementById("create_acct");
    x.style.display = "none";

    var y = document.getElementById("gmail_login");
    var z = document.getElementById("fb_login");
    var w = document.getElementById("login_text");


    y.style.display = "block";
    z.style.display = "block";
    w.style.display = "block";

    console.log('done!!!!');
}


function gmail_login(openid) {

    console.log('start gmail login');
    console.log(openid);

    var u = openid.search('<username>');

    console.log(u);

    if (u != -1) {
        // if openid requires username
        var user = prompt('Enter your Google username:');
        openid = openid.substr(0, u) + user;
        console.log(openid);
    }

    console.log(openid);


//    $.post('/f_login', {url:openid});

   var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "/f_login");

    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("name", "url");
    hiddenField.setAttribute("value", openid);
    form.appendChild(hiddenField);

    document.body.appendChild(form);
    form.submit();



//    window.location.replace("/f_login");

//    document.submit();


    //this has to display errors and info
    //then it needs to recalculate subs list and entries

    console.log('done!!!!');
    return false;
}








function fb_login() {

    console.log('start FB login');
    console.log('done!!!!');
}