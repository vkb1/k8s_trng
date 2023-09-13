# python3.6

import random
from gcp_mqtt_client import get_client
from paho.mqtt import client as mqtt_client
import os

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger()

broker = 'ia_mqtt_broker'
port = 1883
topic = os.getenv("DEVICE_ID")

# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, gcp_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        jwt_iat = datetime.datetime.now(tz=datetime.timezone.utc)
        jwt_exp_mins = 60
        gcp_client.connect(mqtt_host, mqtt_port, 60)
        gcp_client.loop_start()
        gcp_client.publish(msg.topic, msg.payload.decode())
        gcp_client.disconnect()
        gcp_client.loop_stop()

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    project_id=os.getenv("PROJECT")
    cloud_region=os.getenv("CLOUD_REGION")
    registry_id=os.getenv("REGISTRY_ID")
    device_id=os.getenv("DEVICE_ID")
    private_key_file="/gcp_certs/private_key_Intel_Edge_PoC.pem"
    algorithm="RS256"
    ca_certs="/gcp_certs/roots.pem"
    mqtt_bridge_hostname="adani-mqtt.clearblade.com"
    mqtt_bridge_port=8883            
    gcp_mqtt_topic = f"/devices/{device_id}/"

    gcp_client = get_client(
            project_id,
            cloud_region,
            registry_id,
            device_id,
            private_key_file,
            algorithm,
            ca_certs,
            mqtt_bridge_hostname,
            mqtt_bridge_port,
        )
    subscribe(client, gcp_client)
    client.loop_forever()

if __name__ == '__main__':
    run()
