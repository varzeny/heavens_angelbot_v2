import json



how = "Status: Arrived at g_24 BatteryVoltage: 13.0 Location: 7038 -8342 0 Temperature: -127"


i = [ how.find("Status:"), how.find("BatteryVoltage:"), how.find("Location"), how.find("Temperature:") ]

data = [ how[:i[1]], how[i[1]:i[2]], how[i[2]:i[3]], how[i[3]:] ]

# dic = {}
# for s in data:
#     k, v = s.split(':')

#     dic[k.strip()] = v.strip()

dic = { k.strip():v.strip() for k, v in (s.split(':') for s in data) }
print(dic)

status = {
    "status":None,
    "battery":None,
    "location":{},
    "temperature":None
}
status["status"] = dic["Status"]
status["battery"] = int(float(dic["BatteryVoltage"]))
status["location"]["x"] = int((dic["Location"].split(' '))[0])
status["location"]["y"] = int((dic["Location"].split(' '))[1])
status["location"]["z"] = int((dic["Location"].split(' '))[2])
status["temperature"] = dic["Temperature"]

print(status)