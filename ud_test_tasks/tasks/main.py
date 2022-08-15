import datetime
import time
from datetime import timedelta

from rq import Queue
from redis import Redis
from fl_tasks import update_data
from rq_scheduler import Scheduler

REPEAT_INTERVAL = 20

redis_conn = Redis(host='redis', port=6379)


scheduler = Scheduler(connection=redis_conn)

scheduler.schedule(datetime.datetime.utcnow(), func=update_data,  interval=REPEAT_INTERVAL)
