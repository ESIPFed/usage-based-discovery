from flask import render_template, session
from util import graph_db


def parse_stats(app_stat_keys, app_list):
    app_stats = {}
    for app_stat_key in app_stat_keys:
        key_stats = {}
        for app in app_list:
            if app_stat_key in app:
                stat_value = None
                if isinstance(app[app_stat_key], list):
                    stat_value = app[app_stat_key][0]
                else:
                    stat_value = app[app_stat_key]
                if stat_value in key_stats:
                    key_stats[stat_value] += 1
                else:
                    key_stats[stat_value] = 1
        key_stats = {k: v for k, v in sorted(
            key_stats.items(), key=lambda x: x[1], reverse=True)}
        app_stats[app_stat_key] = key_stats
    return app_stats


def leader_board():
    orcid = None
    in_session = 'orcid' in session
    if in_session:
        orcid = session['orcid']

    g = graph_db.GraphDB()
    leader_board_data = g.get_leader_board()

    stat_keys = ['discoverer', 'verifier']

    app_list = leader_board_data['apps']
    app_stats = parse_stats(stat_keys, app_list)

    uses_list = leader_board_data['uses']
    uses_stats = parse_stats(stat_keys, uses_list)

    return render_template('leader-board.html', stats={'apps': app_stats, 'datasets': uses_stats}, in_session=in_session, orcid=orcid)


def about():
    in_session = 'orcid' in session
    return render_template('about.html', in_session=in_session)


def explore():
    in_session = 'orcid' in session
    g = graph_db.GraphDB()
    data = g.get_data()
    return render_template('graph.html', data=data, in_session=in_session)


def bind(flask_app):

    # About page
    flask_app.add_url_rule('/about', view_func=about)

    flask_app.add_url_rule('/explore', view_func=explore)

    flask_app.add_url_rule(
        '/leader-board', view_func=leader_board, methods=["GET"])
