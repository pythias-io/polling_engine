# polling_engine
Opinion polling sent via messaging in natural language

## What it does
this service is implemented as a Redis Pub/Sub client. it does:

1. receive message from redis pubsub
2. run sentiment analysis on the message
3. update db (mysql) with sentiment values for message
4. tally total sentiment scores and keep track on redis store
