'''
@author: YU
'''

'''
@author: YU
'''
import json;
import requests;
import time;
import sched;
import os, glob, time, sys, datetime
import  RPi.GPIO as GPIO
import urllib2



#initiate the temperature sensor & LED
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)

s = sched.scheduler(time.time, time.sleep)


def sendData(temperature, config):
    url = "http://kenari-printee.rhcloud.com/api/temperatures"
    max = config['max_threshold']
    min = config['min_threshold']
    cycle = config['cycle_time']
    if temperature > max or temperature < min:
        os.system("raspistill -o photo.jpg") #
        with open("photo.jpg", "rb") as image_file:
            snapshoot = base64.b64encode(image_file.read())
        data = {
                'temperature_c': temperature,
                'minus_threshold': max,
                'plus_threshold': min,
                'is_alarm': 1,
                'description': "Fire!!",
                'snapshot_url': snapshoot,
                'is_active':1
                }
            GPIO.output(10.True)
            GPIO.output(8.False)
    else:
        data = {'temperature_c': temperature, 'minus_threshold': min, 'plus_threshold': max, 'is_alarm':0}
        GPIO.output(10.False)
        GPIO.output(8.True)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print (temperature, MIN, MAX, alarm)
    time.sleep(cycle)


def read_temp_raw():
    tfile = open("/sys/bus/w1/devices/28-000005ae0321/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    return temperature

def getSetting():
    response = urllib2.urlopen("https://kenari-printee.rhcloud.com/api/temperatures/config/1")
    data = json.load(response)
    return data

while True: #infinite loop
    temp = read_temp_raw() #get the temp
    config = getSetting()
    sendData(temp, config)

