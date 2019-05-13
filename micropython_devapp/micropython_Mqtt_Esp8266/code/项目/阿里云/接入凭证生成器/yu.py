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
