#: whether or not to re-read the bathymetry on the next run.
from datetime import timedelta
import mongoengine
mongoengine.register_connection('cera','cera')

RECALCULATE_BATHYMETRY = False
BATHYMETRY_SOURCE_FILE = '/Users/jeffersonheard/Source/ga-1.4/ga/cera/adcirc.asc'
BATHYMETRY_INDEX_FILE = '/Users/jeffersonheard/Source/ga-1.4/ga/cera/'

#: path that the NetCDF output is mounted to.  no slash on the end of this one
ADCIRC_MOUNTPOINT = '/Users/jeffersonheard/dap'

#: path to the model run NetCDFs
ADCIRC_NETCDF_PATH = '/ncfs/opendap/data/blueridge.renci.org:2/PADCSWAN/nc6b/WNAMAW12-NCP/{yyyymmdd}/{runid}/'
DATASET_DIMENSIONS = (u'time',u'node')

#: valid run ids.  corresponds to hours of the day.
VALID_RUN_ID = ('00','06','12','18')

MAXIMUM_CACHE_SIZE = 50000
DELETE_ARRAYS_OLDER_THAN = timedelta(days=365)

#: variables to find.  uncomment any of these others once we get to wanting them.
VARIABLES = {
#    "statelev"      : "water surface elevation stations",
#    "statatmpress"  : "atmospheric pressure stations",
#    "statwvel"      : "wind velocity stations",
    "atmpress"      : "barometric pressure",
    "maxhsign"      : "maximum significant wave height",
    "dir"           : "mean wave direction",
    "maxradstress"  : "maximum wave radiation stress",
    "dvel"          : "water current velocity",
    "maxtmm10"      : "maximum mean wave period",
    "tmm10"         : "mean wave period",
    "elev"          : "elevation",
    "maxtps"        : "maximum peak wave period",
    "tps"           : "peak wave period",
    "hsign"         : "significant wave height",
    "maxwvel"       : "maximum wind velocity",
    "wvel"          : "wave elevation",
    "maxdir"        : "maximum mean wave direction",
    "minatmpress"   : "minimum atmospheric pressure",
    "maxelev"       : "maximum elevation",
}

from celery.schedules import crontab

# regular tasks to perform.
APP_CELERYBEAT_SCHEDULE = {
    'cera-append_new_run' : {
        'task' : 'cera.tasks.add_new_run',
        'schedule' : crontab(minute=5, hour=[0,6,12,18])
    },
    'cera-clean_web_cache' : {
        'task' : 'cera.tasks.clean_web_cache',
        'schedule' : crontab(minute=0, hour=[0,6,12,18])
    },
    'cera-remove_old_data' : {
        'task' : 'cera.tasks.remove_old_data',
        'schedule' : crontab(day_of_week=0, hour=1, minute=0)
    }
}

APP_LOGGERS = {
    'cera.tasks' : {
        'handlers' : ['console'],
        'propagate' : True,
        'level' : 'DEBUG'
    },
    'cera.query' : {
        'handlers' : ['console'],
        'propagate' : True,
        'level' : 'DEBUG'
    },
    'cera.views' : {
        'handlers' : ['console'],
        'propagate' : True,
        'level' : 'DEBUG'
    }
}
