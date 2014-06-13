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
import spidev



#initiate the temperature sensor & LED
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)

s = sched.scheduler(time.time, time.sleep)


def sendData(temp, noise):
    url_temp = "http://kenari-printee.rhcloud.com/api/temperatures"
    url_noise = "http://kenari-printee.rhcloud.com/api/noises"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url_temp, temp=json.dumps(data), headers=headers)
    r2 = requests.post(url_noise, noise=json.dumps(data), headers=headers)
    time.sleep(cycle)

def DataAnalysis(): #alalysis collected data and sending message to back-end base on the result
    noise = ReadChannel(1)
    temperature = ReadTemp()
    if NoiseIsGood() and TempIsGood():
        temp_data = {'temperature_c': temperature,'is_alarm': 0}
        noise_data = {'noises': noise, 'is_alarm':0}
    else if NoiseIsGood():
        temp_data = {'temperature_c': temperature,'is_alarm': 1}
        noise_data = {'noises': noise, 'is_alarm':0}
    else if TempIsGood():
        temp_data = {'temperature_c': temperature,'is_alarm': 0}
        noise_data = {'noises': noise, 'is_alarm':1}
    else:
        temp_data = {'temperature_c': temperature,'is_alarm': 1}
        noise_data = {'noises': noise, 'is_alarm':1}

def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

def NoiseIsGood():
    response = urllib2.urlopen("http://kenari-printee.rhcloud.com/api/noises/config/1")
    data = json.load(response)
    threshold= config['threshold']
    cycle = config['cycle_time']
    noise = ReadChannel(1)
    if noise < threhold:
        return True
    else:
        return False

def TempIsGood():
    response = urllib2.urlopen("http://kenari-printee.rhcloud.com/api/temperature/config/1")
    data = json.load(response)
    max = config['max_threshold']
    min = config['min_threshold']
    cycle = config['cycle_time']
    temperature = ReadTemp()
     if temperature > max or temperature < min:
        return True
    else:
        return False


def ReadTemp():
    tfile = open("/sys/bus/w1/devices/28-000005ae0321/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    return temperature

while True: #infinite loop
    DataAnalysis()
    sendData()

