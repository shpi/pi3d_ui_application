import os
import sys
import logging

from .. import config
from ..core import peripherals

try:
    import paho.mqtt.publish as mqtt_publish  # NB this insn't used PG
    import paho.mqtt.client as mqtt
except ImportError:
    logging.critical("Please run: (sudo) pip3 install paho-mqtt")
    sys.exit()

client = None


def publishall():
    global client
    try:
        for path in vars(peripherals.eg_object):
            if path == 'led':
                client.publish(config.MQTT_PATH + "/" + path,
                               (str)(getattr(peripherals.eg_object, path)))
            else:
                client.publish(config.MQTT_PATH + "/" + path,
                               getattr(peripherals.eg_object, path))
    except:
        pass


def publish(path, value):
    global client
    try:
        result, mid = client.publish(config.MQTT_PATH + "/" + path, value)
        if result == mqtt.MQTT_ERR_SUCCESS:
                        logging.info("Message {} queued successfully.".format(mid))
        else:
                        logging.error("Failed to publish message. Error: {}".format(result))
                
    except Exception as e:
                    logging.error("EXCEPTION RAISED: {}".format(e))
    
              
    
    
    
    


def on_connect(client, userdata, flags, rc):
    logging.debug("Connected to MQTT broker")
    
    
    
def on_disconnect(client, userdata, flags, rc):
    if rc != 0:
         logging.debug("Lost conncetion to MQTT broker")    


def on_message(client, userdata, message):
    if True: #config.MQTT_SERVER != "mqtt.eclipse.org":  # deactivate for demo server
        msg = message.payload.decode("utf-8")
        logging.debug("message received: {}".format(msg))
        logging.debug("message topic={}".format(message.topic))
        logging.debug("message qos={}".format(message.qos))
        logging.debug("message retain flag={}".format(message.retain))
        if message.topic.startswith(config.MQTT_PATH + "/set/"):
            key = message.topic.split("/")[-1]
            r = peripherals.control(key, msg)
            logging.debug(r)


def init():
    global client
    client = mqtt.Client()
    if len(config.MQTT_USER) and len(config.MQTT_PW):
        client.username_pw_set(config.MQTT_USER, config.MQTT_PW)

    client.connect(config.MQTT_SERVER, config.MQTT_PORT, 60)
    client.loop_start()
    client.subscribe(config.MQTT_PATH + "/set/relay1", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/relay2", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/relay3", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/buzzer", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/d13", qos=config.MQTT_QOS)
    #client.subscribe(MQTT_PATH + "/hwb", qos=0)
    client.subscribe(config.MQTT_PATH + "/set/alert", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/max_backlight",
                     qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/set_temp", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/vent_pwm", qos=config.MQTT_QOS)
    client.subscribe(config.MQTT_PATH + "/set/led", qos=config.MQTT_QOS)

    client.on_connect = on_connect
    client.on_message = on_message
