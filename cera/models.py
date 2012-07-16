from django.db import models
import mongoengine as m

# Create your models here.

class Variable(m.Document):
    basename = m.StringField()
    name = m.StringField()
    long_name = m.StringField()

    meta = {
        "indexes" : ['basename','name']
    }

class ModelRun(m.Document):
    when = m.DateTimeField()
    name = m.StringField(unique=True)
    version = m.StringField()
    hold = m.BooleanField(default=False)

    meta = {
        "indexes" : ['when','name'],
        'db_alias' : 'cera'
    }

    def __unicode__(self):
        return "{name}.{when}".format(name=self.name, when=self.when)


class DataArray(m.Document):
    basename = m.StringField()
    name = m.StringField()
    time = m.DateTimeField()
    data = m.BinaryField()
    long_name = m.StringField()
    version = m.StringField()
    hold = m.BooleanField(default=False)

    meta = {
        "indexes" : [("basename","name"), ('basename','name','time'), ("time", "hold")],
        'db_alias' : 'cera'
    }

    def __unicode__(self):
        return "DataArray<{basename}.{name}> @ {time}".format(
            basename = self.basename,
            name = self.name,
            time = self.time
        )

class StaticArray(m.Document):
    name = m.StringField()
    long_name = m.StringField()
    data = m.BinaryField()

    def __unicode__(self):
        return "StaticArray<{long_name}>".format(long_name=self.long_name)
