import connexion
import yaml
import json
import logging.config
from flask_cors import CORS, cross_origin
from pykafka import KafkaClient

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def get_rr_offset(offset):
    client = KafkaClient(hosts=app_config['datastore']['server'] + ':' + str(app_config['datastore']['port']))
    topic = client.topics[app_config['datastore']['topic']]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)
    msg_list = []
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg_dict = json.loads(msg_str)
        if msg_dict['type'] == 'rr':
            msg_list.append(msg_dict['payload'])
    if offset < len(msg_list):
        print(msg_list[offset])
        response = msg_list[offset]
    else:
        response = "Out of range"

    logger.debug("Renting Request Message List: " + str(msg_list))

    return response, 200


def get_cbs_offset(offset):
    client = KafkaClient(hosts=app_config['datastore']['server'] + ':' + str(app_config['datastore']['port']))
    topic = client.topics[app_config['datastore']['topic']]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)
    msg_list = []
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg_dict = json.loads(msg_str)
        if msg_dict['type'] == 'cbs':
            msg_list.append(msg_dict['payload'])
    if offset < len(msg_list):
        response = msg_list[offset]
    else:
        response = "Out of range"

    logger.debug("Charging Box Statue Message List: " + str(msg_list))

    return response


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    app.run(port=8200)
