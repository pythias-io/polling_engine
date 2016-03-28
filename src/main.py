import sys
import redis
import logging
import threading
from polling_engine.src import config
from polling_engine.src import core


class Listener(threading.Thread):

    def __init__(self, rds, channels):
        threading.Thread.__init__(self)
        self.redis = rds
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
    
    def work(self, item):
        print "received {data} from {channel}".format(**item)
        try:
            params = core.normalise(item['data'])
            message = core.Message(str(params))
            message.is_valid()
            if message.valid:
                sentiment = message.get_sentiment()
                if sentiment:
                    message.update(sentiment)
                    message.count(sentiment)
            else:
                print "invalid message - %s" % item

        except Exception, err:
            print "ERROR: %s -- %s" % (str(err), item)

    
    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == config.REDIS_CONFIG['KILL_CODE']:
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                ####
                # use twisted deferreds here
                ####
                self.work(item)

if __name__ == "__main__":
    rds = redis.Redis(**config.REDIS_CONFIG['CONN'])
    client = Listener(rds, [config.REDIS_CONFIG['CHANNEL']])
    client.start()
