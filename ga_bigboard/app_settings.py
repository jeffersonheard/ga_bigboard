from datetime import timedelta

APP_LOGGING = {
    'ga_bigboard.views' : {
        'handlers': ['ga_bigboard'],
        'level': 'INFO',
        'propagate': True,
    }
}

APP_CELERYBEAT_SCHEDULE = {
    'ga_bigboard-reap_old_participants' : {
        'task' : 'ga_bigboard.tasks.reap_old_participants',
        'schedule' : timedelta(minutes=5)
    }
}

USE_ALT_LOGIN = True