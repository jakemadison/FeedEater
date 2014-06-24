from flask import *
from flask import flash, redirect, url_for, request, g, jsonify  # render_template, session,
from flask.ext.login import current_user  # login_user, logout_user, , login_required
from feedeater.config import configs as c
from feedeater.controller import user_manage_feeds

basedir = c.get('basedir')
app = Blueprint('angulartest', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


def before_blueprint_request():
    g.user = current_user

app.before_request(before_blueprint_request)


@app.route('/ang', methods=['GET'])
def ang_test():

    print 'testing angular'

    # return send_file('./display/static/angulartemplates/angulartest.html')
    #
    return make_response(open(basedir+'/display/static/angulartemplates/index.html').read())
    #
    # return app.send_static_file('angular_test.html')


