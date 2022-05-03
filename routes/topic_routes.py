from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import render_template, request, session
from util import usage_types
from util import change_topics
from routes.helper import thumbnail
import os


def get_change_topic():
    in_session = 'orcid' in session
    g = GraphDB()
    topics = sorted(g.get_topics())
    return render_template('change-topic.html', topics=topics, in_session=in_session)


def post_change_topic():
    in_session = 'orcid' in session
    g = GraphDB()

    old_name = request.form['old-name'].strip()
    new_name = request.form['new-name'].strip()

    if request.form['action'] == 'delete':
        topics = sorted(g.get_topics())
        g.delete_topic(old_name)
        alert = {'success': f'{old_name} was deleted.'}
        return render_template('change-topic.html', topics=topics, in_session=in_session, alert=alert)

    edits = []

    if new_name and old_name:
        change_topics.rename(old_name, new_name)
        edits.append(f'Renamed {old_name} to {new_name}.')
    if new_name and not old_name:
        g.add_topic(new_name)
        edits.append(f'Created a new topic named {new_name}.')

    old_path = f'topic/{old_name}.jpg'
    new_path = f'topic/{new_name}.jpg'
    img_path = new_path if new_name else old_path
    did_upload = thumbnail.upload_thumbnail(
        request, dims=(640, 427), img_path=img_path)
    if did_upload:
        edits.append(f'Uploaded a new topic image {img_path}.')

    if new_name and old_name and not did_upload:
        s3 = s3Functions()
        s3.rename_file(os.environ.get('S3_BUCKET'), old_path, new_path)
        edits.append(f'Renamed topic image from {old_path} to {new_path}.')

    topics = sorted(g.get_topics())
    if edits:
        alert = {'success': f'{ " ".join(edits) }'}
        return render_template('change-topic.html', topics=topics, in_session=in_session, alert=alert)
    else:
        alert = {'danger': 'We did not process this change request because the changes requested were invalid or nonexistent.'}
        return render_template('change-topic.html', topics=topics, in_session=in_session, alert=alert), 422


def topics():
    string_type = request.args.get('string_type') or 'all'
    # string_type is in this format: "<type>,<type2>,<type3>"
    Type = string_type.split(',')
    g = GraphDB()
    if string_type == 'all':
        Type = usage_types.values
        string_type = 'all'
    topic_list = sorted(g.get_topics())
    # attatch presigned url to each topic to get a topic icon to display
    s3 = s3Functions()
    screenshot_list = []
    for topic in topic_list:
        screenshot_list.append(s3.create_presigned_url(
            os.environ.get('S3_BUCKET'), 'topic/'+topic+'.jpg'))
    topics_screenshot_zip = zip(topic_list, screenshot_list)
    # in_session determines if the user is logged in, and if so they get their own privileges
    in_session = 'orcid' in session
    role = session['role'] if 'role' in session else None
    return render_template('topics.html', topics_screenshot_zip=topics_screenshot_zip, in_session=in_session, Type=Type, string_type=string_type, role=role)


def topic_attribution():
    in_session = 'orcid' in session
    return render_template('topic-attribution.html', in_session=in_session)


def bind(flask_app):
    flask_app.add_url_rule('/admin/change-topic',
                           view_func=get_change_topic, methods=["GET"])

    flask_app.add_url_rule('/admin/change-topic',
                           view_func=post_change_topic, methods=["POST"])

    # Initial screen
    flask_app.add_url_rule('/', view_func=topics)

    # Topic attribution
    flask_app.add_url_rule('/topic-attribution', view_func=topic_attribution)
