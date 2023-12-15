#!/usr/bin/python

import pyaudio
import time
import audioop
import wave
import socket


p=pyaudio.PyAudio()
CHUNK = int(44100/60)
frames = []



def callback(in_data, frame_count, time_info, flag):
        global frames, udp
        rms = audioop.rms(in_data, 2)
        print(rms)        
        if rms > 100:
            frames.append(in_data)
            udp.sendto(in_data, ("192.168.1.28", 12345))
            if len(frames) > 60*60:
               writewav(frames)
               frames = []
        elif len(frames) > 60:
            writewav(frames)
            frames = []

        return in_data, pyaudio.paContinue



def writewav(frames):

 print(time.strftime("write: %Y-%m-%d_%H:%M:%S_")+str(int(len(frames)/60)) +'s.wav')
 waveFile = wave.open('/home/pi/recordings/' + time.strftime("%Y-%m-%d_%H:%M:%S_")+str(int(len(frames)/60)) +'s.wav', 'wb')
 waveFile.setnchannels(1)
 waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
 waveFile.setframerate(44100)
 waveFile.writeframes(b''.join(frames))
 waveFile.close()




udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

stream=p.open(format=pyaudio.paInt16,channels=1,rate=44100,
              input=True, input_device_index = 0,frames_per_buffer=CHUNK,stream_callback=callback)



stream.start_stream()

while stream.is_active():
    time.sleep(0.1)



