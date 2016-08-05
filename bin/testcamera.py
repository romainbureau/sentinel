from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 300
camera.start_preview()
sleep(60)
camera.stop_preview()
