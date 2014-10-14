import flask
import flask_bootstrap

from configobj import ConfigObj
from redmine import Redmine

config = ConfigObj('config.ini')

RM_USER = config['user']
RM_KEY = config['key']
RM_URL = config['url']

PROJ_ID = config['project']

TRACKER_MAP = {'epic': 11,
               'bug': 1,
               'task': 12,
               'not-epic': '!11'}

redmine = Redmine(RM_URL, username=RM_URL, key=RM_KEY,
                  requests={'verify': False})


def get_issues(proj, tracker, **kwargs):
    issues = redmine.issue.filter(project_id=proj,
                                  status_id='open',
                                  sort='priority:desc',
                                  tracker_id=TRACKER_MAP[tracker],
                                  **kwargs)

    return issues


def index(user_id=None):
    epics = get_issues(PROJ_ID, 'epic')
    issues = {}
    issues[0] = []

    if user_id:
        i_tmp = get_issues(PROJ_ID, 'not-epic', assigned_to_id=user_id)
    else:
        i_tmp = get_issues(PROJ_ID, 'not-epic')

    for epic in epics:
        issues[int(epic.id)] = []

    for i in i_tmp:
        try:
            parent = int(i.parent)
        except:
            parent = 0
        issues[parent].append(i)

    return flask.render_template('index.html', epics=epics, issues=issues,
                                 url=RM_URL)


def create_app(configfile=None):
    app = flask.Flask('red-list')
    flask_bootstrap.Bootstrap(app)
    app.add_url_rule('/', None, index)
    app.add_url_rule('/assigned/<int:user_id>', None, index)

    return app


if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0')
