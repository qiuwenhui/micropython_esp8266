# Micropython_Mqtt_Esp8266开发

## 参考

协议官网：http://mqtt.org/



​	协议请查看《MQTT协议》

### Micropython WIKI

<http://wiki.micropython.org/Home>

### 库Lib

官方库：<https://github.com/micropython/micropython-lib>

案例

<https://github.com/peterhinch/micropython-mqtt>

<https://github.com/peterhinch/micropython-iot>

参考教程案例

<https://micropython-iot-hackathon.readthedocs.io/en/latest/>

## 测试服务端

MQTT服务软件

mosquitto

mosquito-Client

电脑：Ubuntu 18.04LTS

详情请看《MQTT协议/Mosquitto服务器安装》

## 客户端

### umqtt.simple

参考：<https://github.com/micropython/micropython-lib/tree/master/umqtt.simple#api-design>

安装：<https://pypi.org/project/micropython-umqtt.simple/>

umqtt是MicroPython的简单MQTT客户端。（请注意，它使用了一些MicroPython快捷方式，但不能与CPython一起使用）。

#### API设计

根据上述要求，有以下API特征：

- 与MQTT消息相关的所有数据都被编码为字节。这包括消息内容和主题名称（即使MQTT规范声明主题名称是UTF-8编码）。原因很简单：通过网络套接字接收的是二进制数据（字节），并且需要额外的步骤将其转换为字符串，花费内存。请注意，这仅适用于主题名称（因为它们可以同时发送和接收）。MQTT指定为UTF-8编码的其他参数（例如ClientID）被接受为字符串。
- 订阅的消息通过回调传递。这是为了避免使用队列来订阅消息，否则它们可能在任何时候被接收（包括当客户端期望其他类型的服务器响应时，因此有2种选择：通过回调立即传送它们或排队直到“预期的”反应到了）。请注意，不需要队列是妄想的：在这种情况下，运行时调用堆栈形成一个隐式队列。与显式队列不同，控制起来要困难得多。选择此设计是因为在处理订阅消息的常见情况下，它是最有效的。但是，如果在订阅回调中，QoS> 0的新消息被发布，这可能导致深度或无限递归（后者意味着应用程序将终止`RuntimeException`）。

#### API参考

考虑到上面描述的API特性，umqtt非常接近MQTT控制操作，并将它们映射到类方法：

- `connect(...)` - 连接到服务器。如果此连接使用存储在服务器上的持久会话，则返回True（如果使用clean_session = True参数，则返回False（默认值））。
- `disconnect()` - 断开与服务器的连接，释放资源。
- `ping()` - Ping服务器（响应由wait_msg（）自动处理）。
- `publish()` - 发布消息。
- `subscribe()` - 订阅主题。
- `set_callback()` - 为收到的订阅消息设置回调。
- `set_last_will()` - 设置MQTT“last will”消息。应该*在* connect（）*之前*调用 。
- `wait_msg()` - 等待服务器消息。订阅消息将通过set_callback（）传递到回调集，任何其他消息都将在内部处理。
- `check_msg()` - 检查服务器是否有待处理的消息。如果是，则以与wait_msg（）相同的方式处理，否则立即返回。

`wait_msg()`并且`check_msg()`是“主循环迭代”方法，阻塞和非阻塞版本。`wait_msg()`如果您没有执行任何其他前台任务（即您的应用程序只对订阅的MQTT消息作出反应），`check_msg()` 如果您也处理其他前台任务，则应定期在循环中调用它们 。

请注意，如果您只发布消息，则不需要调用`wait_msg()`/ `check_msg()`，也不要订阅消息。

有关API的更多详细信息，请参阅源代码（这是非常简短易于查看）并提供了示例。

#### simple.py

https://pypi.org/project/micropython-umqtt.simple/

订阅

##### example_sub.py

```python
import time
from umqtt.simple import MQTTClient

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))

def main(server="192.168.31.244"):
    c = MQTTClient("umqtt_client", server)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"foo_topic")
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

```

发布

##### example_pub.py

```python
from umqtt.simple import MQTTClient

# Test reception e.g. with:
# mosquitto_sub -t foo_topic

def main(server="192.168.31.244"):
    c = MQTTClient("umqtt_client", server)
    c.connect()
    c.publish(b"foo_topic", b"hello from micropython")
    c.disconnect()

if __name__ == "__main__":
    main()
```

##### 实例

###### example_sub_led.py

```python
from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython


# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
led = Pin(2, Pin.OUT, value=1)

# Default MQTT server to connect to
SERVER = "192.168.31.244"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"led"


state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(0)
        state = 1
    elif msg == b"off":
        led.value(1)
        state = 0
    elif msg == b"toggle":
        # LED is inversed, so setting it to current state
        # value will make it toggle
        led.value(state)
        state = 1 - state


def main(server=SERVER):
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))

    try:
        while 1:
            #micropython.mem_info()
            c.wait_msg()
    finally:
        c.disconnect()
```

###### example_pub_adc.py

```python
import time
import ubinascii
import machine
import umqtt_simple
from umqtt.simple import MQTTClient
from machine import Pin


# Many ESP8266 boards have active-low "flash" button on GPIO0.
button = Pin(0, Pin.IN)
adc=machine.ADC(0)
# Default MQTT server to connect to
SERVER = "192.168.31.244"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"led"


def main(server=SERVER):
    c = MQTTClient(CLIENT_ID, server)
    c.connect()
    print("Connected to %s, waiting for button presses" % server)
    while True:
        adc_value=adc.read()
        print("adc_value = %d",adc_value)
        adc_value="adc_value = "+str(adc_value)
        c.publish(TOPIC, adc_value.encode("utf-8"))
        time.sleep_ms(200)

    c.disconnect()
```


### microhomie 0.3.1

参考：<https://pypi.org/project/microhomie/>

### micropython-mqtt

参考：

<https://github.com/peterhinch/micropython-mqtt>

### micropython-iot

参考

<https://github.com/peterhinch/micropython-iot>

物联网框架

### ThingFlow-python

<https://github.com/mpi-sws-rse/thingflow-python>

## 云端物联网平台

参考

<https://github.com/mqtt/mqtt.github.io/wiki/brokers>

### CloudMQTT 

参考：

[https://www.cloudmqtt.com](https://www.cloudmqtt.com/)

账号

GITHUB账号

软件：<https://github.com/CloudMQTT>

#### 客户端

cloudmqtt.py

```python
#https://www.cloudmqtt.com
#umqtt.simple
import time
from umqtt.simple import MQTTClient

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))

port=12519
user="bnjxtnyp"
passw="2g8dIx_cHIM2"
def main(server="m24.cloudmqtt.com"):
    c = MQTTClient("umqtt_client", server,port,user,passw)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"$SYS/broker/load/connections/+")
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

```

### 连接阿里云IOT

参考

https://help.aliyun.com/product/30520.html

esp8266 for arduino 连接 到阿里云

：https://help.aliyun.com/document_detail/104070.html?spm=a2c4g.11186623.6.777.67b03e3cMLLmQU

案例

https://www.jianshu.com/p/f6b1936d6052

生成文本

```python
#参考https://help.aliyun.com/document_detail/73742.html?#spm=a2c4g.11186623.2.15.71c43f86UoNcMH#h2-url-3
RegionID="cn-shanghai"
ProductKey="a1sWLxJ57zd"
DeviceName="testiot"
DeviceSecret="FMsrkZ0FihebKNzw77s65z6fdM1xGxrk"

#MqttServerAddr
MqttServerAddr=ProductKey+".iot-as-mqtt."+RegionID+".aliyuncs.com"
print(MqttServerAddr)

#MqttClientID
clientid=123345
timestamp=600
MqttClientID=str(clientid)+"|securemode=3,signmethod=hmacsha1,timestamp="+str(timestamp)+"|"
print(MqttClientID)

#UserName
UserName=DeviceName+'&'+ProductKey
print(UserName)

#password
import time
from   hashlib import sha1
import hmac
import base64

deviceSecret=DeviceSecret
content="clientId"+str(clientid)+"deviceName"+DeviceName+"productKey"+ProductKey+"timestamp"+str(timestamp)

print(content)

my_sign = hmac.new(bytes(deviceSecret,encoding='utf-8'),bytes(content,encoding='utf8'),sha1).digest()
password = my_sign.hex()
print(password)

```

#### Esp8266_Micropython

```python
#阿里云
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
```

控制LED 及上报ADC值

```python
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
```

