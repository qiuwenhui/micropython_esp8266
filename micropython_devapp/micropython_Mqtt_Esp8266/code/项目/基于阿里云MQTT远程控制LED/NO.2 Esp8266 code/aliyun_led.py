#https://www.cloudmqtt.com
import time
from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython
# Many ESP8266 boards have active-low "flash" button on GPIO0.
button = Pin(0, Pin.IN)
adc=machine.ADC(0)

# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
led = Pin(2, Pin.OUT, value=1)
# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello

# Received messages from subscriptions will be delivered to this callback

#数据解析 json
import ujson

def get_msg(msg):
    msg=ujson.loads(msg)
    return msg['params']['LightSwitch'] #提取数据
    

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    msg=get_msg(msg)
    if msg == 1:
        led.value(0)
        state = 1
        #c.publish(TOPIC, adc_value.encode("utf-8"))
    elif msg == 0:
        led.value(1)
        state = 0

RegionID="cn-shanghai"
ProductKey="a1KHqogX1Si"
DeviceName="QcOF2EXO50uAWuGvD8QP"
DeviceSecret="Djy1QIjIq5vq74zVNKcPfVU6qpOQIML2"

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

PassWord="232b3d9f791c17e2080464487d9533c8fa4eb948"
print("clientid:",MqttClientID,"\n","ServerAddr:",MqttServerAddr,"\n","User Name:",UserName,"\n","Password:",PassWord,"\n")

TOPIC="/sys/a1KHqogX1Si/QcOF2EXO50uAWuGvD8QP/thing/event/property/post"
a={
  "properties": [
    {
       "WorkState":1
    }
  ]
}
#keepalive=500
def main(server=MqttServerAddr):
    c = MQTTClient(client_id = MqttClientID,server= MqttServerAddr,port=1883,user=UserName, password=PassWord,keepalive=200) 
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"/sys/a1KHqogX1Si/QcOF2EXO50uAWuGvD8QP/thing/service/property/set")
    while True:
        if True:
            # Blocking wait for message
            #c.wait_msg()
            
            send_mseg = '{"params":{"LightSwitch":%s,"CurrentLedADC":%s}}' % (1-led.value(),adc.read())
            c.publish(TOPIC,msg=send_mseg,qos=1, retain=True)
            #time.sleep_ms(10)
        else:
            # Non-blocking wait for message
            c.check_msg()
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep(1)

    c.disconnect()

if __name__ == "__main__":
    main()
