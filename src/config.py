"""
polling_engine configs
"""
import os
LOG_FILE = os.getenv('APPS_HOME') + '/polling_engine/src/logs/poll.log'

REDIS_CONFIG = dict(
        CHANNEL='polling.channel.messages',
        KILL_CODE='4cfadf7f-2823-40f3-9d4c-4d6494f86d42-kill',
        COUNT_KEY=dict(
            POSITIVE='poll.{}.positive',
            NEGATIVE='poll.{}.negative',
            NEUTRAL='poll.{}.neutral'
            ),
        CONN=dict(
            host='localhost',
            port=9738,
            db=0,
            password=os.getenv('REDIS_PASSWORD')
            ),
        )

MYSQL_CONFIG = dict(
        UPDATE="""
        update messages set sentiment_polarity = '%s', 
        sentiment_score = '%s' where messageid = %s
        """,
        
        )
