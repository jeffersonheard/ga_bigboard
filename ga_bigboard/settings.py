from datetime import timedelta

LOGGING = {
    'ga_bigboard.views' : {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    }
}

CELERYBEAT_SCHEDULE = {
    'ga_bigboard-reap_old_participants' : {
        'task' : 'ga_bigboard.tasks.reap_old_participants',
        'schedule' : timedelta(minutes=5)
    }
}