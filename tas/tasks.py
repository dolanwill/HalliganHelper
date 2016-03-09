from __future__ import absolute_import
from celery import shared_task
import logging
import redis

from .utils import publish_message
from .models import OfficeHour

logger = logging.getLogger(__name__)

POOL = redis.ConnectionPool(host='localhost', db=0)

@shared_task
def broadcast_message_later(message_type, data=None):
    logger.info('Broadcasting via celery. message_type="%s" data="%s"',
                message_type, data)
    publish_message(message_type, data)
