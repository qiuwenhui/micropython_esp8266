#https://www.cloudmqtt.com
import time
from umqtt.simple import MQTTClient

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))

RegionID="cn-shanghai"
ProductKey="a1sWLxJ57zd"
DeviceName="testiot"
DeviceSecret="FMsrkZ0FihebKNzw77s65z6fdM1xGxrk"

#MqttServerAddr
MqttServerAddr=ProductKey+".iot-as-mqtt."+RegionID+".aliyuncs.com"
#print(MqttServerAddr)
Port=1883
#MqttClientID
clientid=123345
timestamp=600
MqttClientID=str(clientid)+"|securemode=3,signmethod=hmacsha1,timestamp="+str(timestamp)+"|"
#print(MqttClientID)

#UserName
UserName=DeviceName+"&"+ProductKey
#print(UserName)

PassWord="261b246eb7143b29f09b3b1283691907f2bae7dc"
print("clientid:",MqttClientID,"\n","ServerAddr:",MqttServerAddr,"\n","User Name:",UserName,"\n","Password:",PassWord,"\n")

#keepalive=500
def main(server=MqttServerAddr):
    c = MQTTClient(client_id = MqttClientID,server= MqttServerAddr,port=1883,user=UserName, password=PassWord,keepalive=60) 
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"/a1sWLxJ57zd/testiot/user/get")
    while True:
        if True:
            # Blocking wait for message
            c.wait_msg()
        else:
            # Non-blocking wait for message
            c.check_msg()
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep(1)

    c.disconnect()

if __name__ == "__main__":
    main()

