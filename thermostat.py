import constants

    def init(self):
                   
        text = pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128)    
        temp_block = pi3d.TextBlock(-350, 50, 0.1, 0.0, 15, data_obj=eg_object,attr="act_temp",text_format= chr(0xE021) +"{:2.1f}°C", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
        text.add_text_block(temp_block)

        if heatingrelay or coolingrelay:
            set_temp_block= pi3d.TextBlock(-340, -30, 0.1, 0.0, 15, data_obj=eg_object,text_format= chr(0xE005) + " {:2.1f}°C", attr="set_temp",size=0.5, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
            text.add_text_block(set_temp_block)
            increaseTemp = pi3d.TextBlock(300, 150, 0.1, 180.0, 1, text_format= chr(0xE000),size=0.99, spacing="C", space=0.6, colour=(1, 0, 0, 0.8))
            text.add_text_block(increaseTemp)
            decreaseTemp = pi3d.TextBlock(300, -50, 0.1, 0.0, 1, text_format= chr(0xE000),size=0.99, spacing="C", space=0.6, colour=(0, 0, 1, 0.8))
            text.add_text_block(decreaseTemp)
            cloud = pi3d.TextBlock(-30, -30, 0.1, 0.0, 1  , text_format = chr(0xE002), size=0.5, spacing="C", space=0.6, colour=(1,1,1,0.9))
            text.add_text_block(cloud)

        if ADDR_BMP:
            barometer = pi3d.TextBlock(20, -25, 0.1, 0.0, 2, text_format= chr(0xE00B), size=0.6, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0,0.9))
            text.add_text_block(barometer)
            baroneedle = pi3d.Triangle(camera=CAMERA, corners=((-3,0,0),(0,15,0),(3,0,0)), x=barometer.x+32, y=barometer.y - 12, z=0.1)
            baroneedle.set_shader(matsh)

        newtxt = pi3d.TextBlock(270, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
        text.add_text_block(newtxt)
        motiondetection = pi3d.TextBlock(290, -175, 0.1, 0.0, 15, text_format = chr(0xE01C), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
        text.add_text_block(motiondetection)

        if heatingrelay:
            newtxt = pi3d.TextBlock(145, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
            text.add_text_block(newtxt)
            heating = pi3d.TextBlock(172, -180, 0.1, 0.0, 15, text_format = chr(0xE004), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
            text.add_text_block(heating)

        if coolingrelay:
            newtxt = pi3d.TextBlock(20, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
            text.add_text_block(newtxt)
            cooling = pi3d.TextBlock(42, -182, 0.1, 0.0, 15, text_format = chr(0xE029), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
            text.add_text_block(cooling)


        newtxt = pi3d.TextBlock(-400, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
        text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-385, -180, 0.1, 0.0, 15, text_format = chr(0xE02F), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
        text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-300, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
        text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-275, -180, 0.1, 0.0, 15, text_format = chr(0xE031), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
        text.add_text_block(newtxt)
        
        
        
    def inloop(self,x = 0, y = 0, touch_pressed = False, textchange = False, offset = 0):

        if textchange:
            red = (0.01 * (eg_object.a4/4))
            if (red > 1): red = 1
    
            green = (0.01 * (120 - eg_object.a4/4))
            if green < 0: green = 0
            if green > 1: green = 1
    
            cloud.colouring.set_colour([red, green , 0, 1.0])
    
            if eg_object.pressure:
              normalizedpressure = (eg_object.pressure - 950)
              if normalizedpressure < 0: normalizedpressure = 0
              if normalizedpressure >  100: normalizedpressure = 100
              green = 0.02 * (normalizedpressure)
              if green > 1: green = 1
              red = 0.02 * (100 - normalizedpressure)
              if red > 1: red = 1
              barometer.colouring.set_colour([red, green , 0, 1.0])
              baroneedle.set_material([red,green,0])
              baroneedle.rotateToZ(100 - (normalizedpressure*2))
            text.regen()

        if eg_object.pressure and offset == 0 :
            baroneedle.draw()

        if (eg_object.motion):
            motiondetection.colouring.set_colour([1,0,0])
        else:
            motiondetection.colouring.set_colour([1,1,1])

        if touch_pressed:
			
            activity = True
            
            if heatingrelay or coolingrelay:

                if clicked(increaseTemp.x,increaseTemp.y):
                    controls_alpha = 1
                    eg_object.set_temp += 0.5
                    set_temp_block.colouring.set_colour([1,0,0])

                if clicked(decreaseTemp.x,decreaseTemp.y):
                    controls_alpha  = 1
                    eg_object.set_temp -= 0.5
                    set_temp_block.colouring.set_colour([0,0,1])


            if clicked(-330,-180):
                slide = 0

                try:
                    os.popen('killall omxplayer.bin')
                except:
                    pass

                os.popen('omxplayer --threshold 0.5  --display 4 rtsp://username:pass@192.168.1.5:554/mpeg4cif --win "0 0 800 450"')       
                # loading time depends on keyframes in stream, only h264 recommended!

            if clicked(-230,-180):
                slide = -1

                try:
                    os.popen('killall omxplayer.bin')
                    os.popen('killall raspivid')
                except:
                    pass

                os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@192.168.1.34 "raspivid  -t 0 -w 640 -h 480 -g 10 -ih -fps 25 -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5001"')
                os.popen('raspivid  -t 0 -w 640 -h 480 -g 10  -ih -fps 25 -hf  -vf -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5002')
                os.popen('sleep 1 && nc 192.168.1.34 5001 | ./videoplayer 0 0 640 480')
                os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@192.168.1.34 "nc 192.168.1.50 5002 | ./videoplayer 0 0 640 480"')

        #intercom between 2 SHPIs,  just a test concept,  master access slave and start necessary applications
        #os.popen('arecord -D plughw:1,0 -r 8000 -f S16_LE -c1 -N -B 100 -t wav | nc -l 5002')
        #os.popen('nc [ownip] 5002 | aplay -f S16_LE -c1 -r 8000')
        #sshpass -p 'password' ssh -o StrictHostKeyChecking=no  user@server "arecord -D plughw:1,0 -r 8000 -f S16_LE -c1 -N -B 100 -t wav | nc -l 5002";
        #sshpass -p 'password' ssh -o StrictHostKeyChecking=no  user@server "nc [ownip] 5002 | aplay -f S16_LE -c1 -r 8000";


        if controls_alpha > 0.3:
            activity = True
            controls_alpha -= 0.01
        if heatingrelay or coolingrelay:
            increaseTemp.colouring.set_colour(alpha = controls_alpha)
            decreaseTemp.colouring.set_colour(alpha = controls_alpha)
            set_temp_block.colouring.set_colour(alpha = controls_alpha)
        if controls_alpha < 0.3:
            
            if heatingrelay or coolingrealy:
                set_temp_block.colouring.set_colour([1,1,1])



        if offset != 0:
            offset = slider_change(text.text, offset)
            
            
        text.draw()
         
        return offset




















