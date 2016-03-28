import json
import redis
import requests
import datetime
from polling_engine.src import config
from db_utilities.mysql.core import run_query

def normalise(parameters):
    '''
    '''
    params = eval(parameters)
    channel = params['client']
    if channel == 'twitter':
        new_struct = dict(
                id=params['request_id'],
                text=params['message'],
                name=params['username'],
                user_id=params['sender_id'],
                poll_id=params['poll_id'],
                client='twitter'
                )
    return new_struct


class Message(object):

    def __init__(self, msg):
        try:
            self.msg = eval(msg)
        except Exception, err:
            print "message cannot eval: %s -- %s" % (err, msg)
            self.msg = {}
        self.rds = redis.StrictRedis(**config.REDIS_CONFIG['CONN'])


    def is_valid(self, ):
        self.valid = False
        try:
            assert 'id' in self.msg
            assert 'text' in self.msg
            assert 'name' in self.msg
            assert 'user_id' in self.msg
            assert 'poll_id' in self.msg
            assert 'client' in self.msg
            self.valid = True
        except AssertionError:
            print "something's missing"

    def get_sentiment(self, ):
        '''
        return sentiment polarity and score
        '''
        sentiment = {}
        payload = dict(
                apikey=config.ALCHEMY['API_KEY'],
                text=str(self.msg['text']),
                outputMode='json',
                showSourceText=1
                )
        print "{} - params sending to alchemy: {}".format(self.msg['id'], payload)
        resp = requests.post(config.ALCHEMY['BASE'], params=payload)
        print "{} - Alchemy resp: {}".format(self.msg['id'], str(resp.content))
        if resp.status_code == 200:
            resp_body = json.loads(resp.content)
            if 'docSentiment' in resp_body and resp_body['language'] == 'english':
                sentiment = resp_body['docSentiment']
                if 'type' in resp_body['docSentiment'] and 'score' not in resp_body['docSentiment']:
                    sentiment['score'] = config.ALCHEMY['DEFAULT_POLARITY_SCORES'][(sentiment['type'])]


        print "{} - sentiment result: {}".format(self.msg['id'], sentiment)
        return sentiment


    def update(self, sentiment):
        update_query = config.MYSQL_CONFIG['UPDATE'] % (
                sentiment['type'], sentiment['score'], self.msg['id']
                )
        resp = run_query(update_query, db='sentiments')

        if not resp['ok']:
            print "ERROR: {} update db -- {}".format(self.msg['id'], resp)
        else:
            if 'rows' in resp:
                if resp['rows'] == 0:
                    print "WARNING: {} update db - Entry NOT in DB".format(self.msg['id'])
                else:
                    print "{} - updated db - {}".format(self.msg['id'], resp)

    def count(self, sentiment):
        '''
        updates count on redis
        '''
        polarity = sentiment['type']
        key = config.REDIS_CONFIG['COUNT_KEY'][polarity.upper()]
        resp = self.rds.incr(key.format(self.msg['poll_id']))
        print "{} - incr {} by 1 to {}".format(self.msg['id'], key, resp)
