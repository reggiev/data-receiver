import pika, os


def rmqwriter(exchange, routing_key, data):
    # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
    url = os.environ.get('CLOUDAMQP_URL', "")
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() # start a channel
    channel.basic_publish(exchange=exchange,
                        routing_key=routing_key,
                        body=data)
    connection.close()
