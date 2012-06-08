from celery.task import task
from ga_bigboard import models
import datetime

@task(ignore_result=True)
def reap_old_participants():
    then = datetime.datetime.now() - datetime.timedelta(minutes=5)
    Participant.objects.filter(last_heartbeat__lt=then).delete()