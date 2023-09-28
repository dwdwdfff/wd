from redis import StrictRedis
import logging
logging.getLogger("redis").setLevel(logging.CRITICAL)

db = StrictRedis(decode_responses=True)
