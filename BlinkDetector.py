import cv2
import winsound
import os.path
from wx.lib.pubsub import pub


'''
This allows basic blink detection using template matching.
'''

class BlinkDetector():
    def __init__(self, (screen_width, screen_height), test=False):
        if not (os.path.isfile('eyes.xml') and os.path.isfile('open.png')
                and os.path.isfile('blink.png')):
            msg = ('Basic file needed missing, please check folder for'
                   'eyes.xml, open.png and blink.png')
            pub.sendMessage('Error Message', msg=msg)
            self.init = False
            pub.sendMessage("SwitchInput", msg="closing")
        else:
            self.eye_cascade = cv2.CascadeClassifier('eyes.xml')
            video_src = 0
            self.cam = cv2.VideoCapture(video_src)
            self.COMP_METHOD = 'cv2.TM_CCOEFF_NORMED'
            self.open_eyes = cv2.imread('open.png',0)
            self.shut_eyes = cv2.imread('blink.png',0)
            self.shut_shape = self.shut_eyes.shape
            self.open_shape = self.open_eyes.shape
            self.test = test
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.eyes_open_msg_sent = True
            self.init = True

    def RunDetect(self):
        cv2.imshow("needed for focus", self.shut_eyes)
        cv2.resizeWindow("needed for focus", 20, 20)
        cv2.moveWindow("needed for focus", -100, -100)
        if not self.init:
            return False
        while True:
            ret, img = self.cam.read()
            if ret:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                rects = self.eye_cascade.detectMultiScale(gray, 1.10, 8)
                if len(rects) == 0:
                    #the eyes have not been detected so the whole image
                    #is searched
                    search_image = gray
                    pos = None
                else:
                    #the eyes are currently being detected
                    (search_image, pos) = self.FindEyesRect(img, gray, rects)
                if search_image is not None:
                    #then we search the image to detect blinks
                    blink_pos = self.CheckForBlink(search_image)
                    if blink_pos is not None:
                        self.BlinkFound(pos, img, blink_pos)
                        if self.test:
                            winsound.Beep(2500, 200)
                    else:
                        self.EyesOpenMesssage()
                if self.test:
                    display_img = cv2.resize(img, (0,0), fx=0.4, fy=0.4)
                    xpos = self.screen_width - int(display_img.shape[0]*1.5)
                    ypos = self.screen_height/2  - display_img.shape[1]/2
                    cv2.imshow("full image", display_img)
                    cv2.moveWindow("full image", xpos, ypos)
                key_press = cv2.waitKey(20)
                if key_press == 27:
                    pub.sendMessage("SwitchInput", msg="closing")
                    self.Close()
                    break
            else:
                break
                #this means no camera was found, I will send an error
                #message in this case in the eventual user friendly
                #version of the system

    def FindEyesRect(self, img, gray, rects):
        big_width = 0
        big_height = 0
        search_image = None
        pos = None
        for x, y, width, height in rects:
            if(width > big_width and height > big_height):
                big_width = width
                big_height = height
                pos = (x,y)
        if big_width != 0 and big_height != 0:
            if(big_width < self.shut_shape[1] or
               big_width < self.open_shape[1]):
                  big_width = max(self.shut_shape[1], self.open_shape[1])
            if(big_height < self.shut_shape[0] or
               big_height < self.open_shape[0]):
                  big_height = max(self.shut_shape[0], self.open_shape[0])
            cv2.rectangle(img, (pos[0], pos[1]),
                          (pos[0]+big_width, pos[1]+big_height), (255,0,0), 2)
            search_image = gray[pos[1]:pos[1]+big_height,
                                pos[0]:pos[0]+big_width]
        return (search_image, pos)

    def CheckForBlink(self, search_image):
        method = eval(self.COMP_METHOD)
        shut_res = cv2.matchTemplate(search_image,self.shut_eyes,method)
        min_shut_val, max_shut_val, min_shut_loc, max_shut_loc = \
              cv2.minMaxLoc(shut_res)
        open_res = cv2.matchTemplate(search_image,self.open_eyes,method)
        min_open_val, max_open_val, min_open_loc, max_open_loc = \
              cv2.minMaxLoc(open_res)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            if min_shut_val < min_open_val:
                blink_pos = min_shut_loc
            else:
                blink_pos = None
        else:
            if max_shut_val > max_open_val:
                blink_pos = max_shut_loc
            else:
                blink_pos = None
        return blink_pos

    def BlinkFound(self, pos, img, blink_pos):
        self.eyes_open_msg_sent = False
        if pos is not None:
            blink_pos = (blink_pos[0] + pos[0], blink_pos[1] + pos[1])
        blink_img = img[blink_pos[1]:blink_pos[1]+self.shut_shape[0],
                        blink_pos[0]:blink_pos[0]+self.shut_shape[1]]
        blink_bottom_right = (blink_pos[0] + self.shut_shape[1],
                              blink_pos[1] + self.shut_shape[0])
        cv2.rectangle(img, blink_pos, blink_bottom_right, 255, 2)
        #EVENTUALLY - I want to save the blink_img here if eyes were
        #successfully found, for use in subsequent iterations (to account
        #for small changes in light over time)
        pub.sendMessage("SwitchInput", msg="shut")

    def EyesOpenMesssage(self):
        if not self.eyes_open_msg_sent:
            #inform that the eyes are open again
            self.eyes_open_msg_sent = True
            pub.sendMessage("SwitchInput", msg="open")

    def Close(self):
        cv2.destroyAllWindows()
        self.cam.release()



if __name__ == "__main__":
  
    def listener1(msg): print "message received", msg
    pub.subscribe(listener1, 'SwitchInput')

    def listener2(msg): print "Error:- ", msg
    pub.subscribe(listener2, 'Error Message')

    tester = BlinkDetector((400,400), True)
    tester.RunDetect()
    

