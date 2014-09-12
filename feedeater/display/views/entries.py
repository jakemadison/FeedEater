from flask import *
from flask import redirect, url_for, request, g, jsonify  # , render_template, flash, session
from flask.ext.login import current_user  # , login_user, logout_user, login_required
from feedeater.config import configs as c
from feedeater.controller import user_manage_feeds
from feedeater.controller import user_manage_entries


import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.DEBUG)

basedir = c.get('basedir')
app = Blueprint('entries', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


@app.before_request
def before_request():
    logger.info("NEW ENTRIES REQUEST:")
    g.user = current_user


#####
# Functions for all entries:
#####

@app.route('/recalculate_entries', methods=['POST', 'GET'])
def recalculate_entries():

    logger.info("recalculating entries....")
    user = g.user
    page = int(request.args.get('page_id', None))

    if page is None:
        page = 1

    logger.debug('page: {0}'.format(page))
    g.page = page

    entries, pager, total_records, per_page = user_manage_feeds.recalculate_entries(user, page)
    prefs = user_manage_feeds.get_user_prefs(user)

    return jsonify(success=True, e=entries, compressed_view=prefs, per_page=per_page,
                   pager=pager, total_records=total_records)


@app.route('/get_unread_count', methods=['GET'])
def unread_count():

    user = g.user

    # Ok, so currently this is just using "feed_id", I probably actually want to send "uf_id"

    feed_id = request.args.get('feed', '', type=int)
    logger.debug('feed id: {0}'.format(feed_id))

    result = user_manage_feeds.get_unread_count(feed_id, user)
    logger.debug('result: {0}'.format(result))

    return jsonify(success=True, count=result)


#####
# Functions for single entries:
#####

@app.route('/tags', methods=['POST'])
def change_tags():

    user = g.user
    tag_text = request.form['tagtext']
    tag_id = request.form['tagid']

    logger.info('tag_text: {0}, tag_id: {1}'.format(tag_text, tag_id))

    if g.user.is_authenticated():
        tags = user_manage_entries.change_user_tags(user)
    else:
        return redirect(request.args.get('next') or url_for('index'))

    return jsonify(title='Home', tags=tags)


@app.route('/star', methods=['POST'])
def toggle_star():

    user = g.user
    entryid = request.form['starid']
    entryid = entryid[5:]
    logger.debug('entry_id: {0}'.format(entryid))

    # right.. so before i made the decision to only add an entry when needed..

    result = user_manage_entries.change_star_state(user, entryid)

    logger.debug('result: {0}'.format(result))

    return jsonify({"result": result})


@app.route('/mark_as_read', methods=['POST'])
def markAsRead():
    user = g.user
    entry_id = request.form['entry_id']
    logger.info('marking entry: {e} as read for user: {u}'.format(e=entry_id, u=user.nickname))

    user_manage_entries.mark_entry_read(entry_id, user.id)

    return jsonify(success=True)







