import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

MQTT_PUB_TOPIC = "mobile/lhhlhh0105/sensing"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe("trashcan/status")

def on_message(client, userdata, message):
    result = str(message.payload.decode("utf-8"))
    sensing = json.loads(result)
    print(message.topic + " " +str(message.payload))
    
    
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

GPIO.setmode(GPIO.BCM)

BUTTON = 22

Red_LED = 23
Yellow_LED = 24
Green_LED = 25

TRIG = 13
ECHO = 19

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Red_LED, GPIO.OUT)
GPIO.setup(Yellow_LED, GPIO.OUT)
GPIO.setup(Green_LED, GPIO.OUT)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time
    distance = time_elapsed * 17000
    distance = round(distance, 2)

    return distance

def conver_to_percentage(distance, max_distance):
    if distance <= 0:
        percentage = 100
    elif distance >= max_distance:
        percentage = 0
    else:
        percentage = ((max_distance - distance) / max_distance) * 100
    return round(percentage, 2)

try:
    while True:
        distance_m = measure_distance()
        percentage = conver_to_percentage(distance_m, 50)
        
        button_state = GPIO.input(BUTTON)
        if button_state == True:
            print("Distance:",distance_m)
            client.publish(MQTT_PUB_TOPIC, "현재 쓰레기통 상태 :" + str(percentage) + "%")
        
        # 거리에 따라 LED 제어
        if distance_m > 30:
            GPIO.output(Green_LED, GPIO.HIGH)
            GPIO.output(Yellow_LED, GPIO.LOW)
            GPIO.output(Red_LED, GPIO.LOW)
        elif 10 < distance_m <= 30:
            GPIO.output(Green_LED, GPIO.LOW)
            GPIO.output(Yellow_LED, GPIO.HIGH)
            GPIO.output(Red_LED, GPIO.LOW)
        else:
            GPIO.output(Green_LED, GPIO.LOW)
            GPIO.output(Yellow_LED, GPIO.LOW)
            GPIO.output(Red_LED, GPIO.HIGH)
        time.sleep(1)
        
        
except KeyboardInterrupt:
    print("사용자가 프로그램을 종료했습니다.")