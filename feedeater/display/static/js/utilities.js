function subClick() {
    pageid = document.getElementById("url");
}


function set_openid_new(openid, pr)
{
    u = openid.search('<username>')
    if (u != -1) {
        // openid requires username
        user = prompt('Enter your ' + pr + ' username:')
        openid = openid.substr(0, u) + user
    }
    form = document.forms['login_form'];
    form.elements['openid'].value = openid
}