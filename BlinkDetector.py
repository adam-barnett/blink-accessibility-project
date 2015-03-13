import cv2
import winsound
import os
from wx.lib.pubsub import pub
import win32gui, win32con
import math


'''
This allows basic blink detection using template matching.
if test is set to True then the system will beep when a blink is detected
if features is set to True then the haar cascades for the face and eyes will
be used to narrow the area in which the template matching happens.  The effects
of this are that it slows the system down somewhat (about 100ms per iteration)
but improves the accuracy if the images of the eyes are not good (i.e. they
were taken at a different time of day).
'''

class BlinkDetector():
    def __init__(self, (screen_width, screen_height), test=False,
                 use_features=None):
        if not (os.path.isfile('eyes.xml')
                and os.path.isfile('left_open.png')
                and os.path.isfile('left_closed.png')
                and os.path.isfile('right_open.png')
                and os.path.isfile('right_closed.png')
                and os.path.isfile('nose.png')
                and os.path.isfile('face.xml')):
            msg = ('Basic file needed missing, please check folder for'
                   'the images (nose.png, left_closed.png, left_open.png'
                   'right_closed.png, right_open.png')
            pub.sendMessage('Error Message', msg=msg)
            self.init = False
            pub.sendMessage("SwitchInput", msg="closing")
        else:
            self.eye_cascade = cv2.CascadeClassifier('eyes.xml')
            self.face_cascade = cv2.CascadeClassifier('face.xml')
            video_src = 0
            self.blink_correction = 0.015
            self.blink_threshold = 0.7
            self.cam = cv2.VideoCapture(video_src)
            self.COMP_METHOD = 'cv2.TM_CCOEFF_NORMED'
            self.open_eyes = cv2.imread('left_open.png', 0)
            self.shut_eyes = cv2.imread('left_closed.png', 0)
            cv2.imshow('open', self.open_eyes)
            cv2.imshow('closed', self.shut_eyes)
            self.shut_shape = self.shut_eyes.shape
            self.open_shape = self.open_eyes.shape
            self.terminate = True
            self.test = test
            if self.test:
                self.open_vals = []
                self.close_vals = []
            self.use_features = use_features
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.eyes_open_msg_sent = True
            self.init = True

    def RunDetect(self):
        self.terminate = False
        cv2.imshow("needed for focus", self.shut_eyes)
        cv2.resizeWindow("needed for focus", 20, 20)
        cv2.moveWindow("needed for focus", -100, -100)
        if not self.init:
            return False
        while True:
            ret, img = self.cam.read()
            if ret:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                if self.use_features == 'face':
                    search_image = gray
                    pos = None
                    """
The following code is currently removed because the face cascade is too slow
but it may be needed in future for size invariance.  Ideally it will be
activated once every 5 iterations or something similar
"""
##                    rects = self.face_cascade.detectMultiScale(gray,1.10,8)
##                    if len(rects) != 1:
##                        #the eyes and face have not been detected so the
##                        #whole image must be searched
##                        search_image = gray
##                        pos = None
##                    else:
##                        [x, y, width, height] = rects[0]
##                        cv2.rectangle(img, (x, y), (x+width, y+height),
##                                      (0,0,255), 2)
##                        search_rect = self.EyesFromFace(rects[0])
##                        (search_image, pos) = self.SearchImageFromRect(
##                                                    img, gray, search_rect)
                elif self.use_features == 'eyes':
                    rects = self.eye_cascade.detectMultiScale(gray, 1.10, 8)
                    if len(rects) == 0:
                        #the eyes and face have not been detected so the
                        #whole image must be searched
                        search_image = gray
                        pos = None
                    else:
                        #the eyes are currently being detected
                        (search_image, pos) = self.SearchImageFromRect(
                                                        img, gray, rects)
                else:
                    search_image = gray
                    pos = None
                if search_image is not None:
                    #then we search the image to detect blinks
                    blink_pos = self.CheckForBlink(search_image)
                    if blink_pos is not None:
                        self.BlinkFound(pos, img, blink_pos)
                        winsound.Beep(2500, 50)
                    else:
                        self.EyesOpenMesssage()
                display_img = cv2.resize(img, (0,0), fx=0.7, fy=0.7)
                xpos = self.screen_width - int(display_img.shape[0]*1.5)
                ypos = self.screen_height/3  - display_img.shape[1]/2
                cv2.imshow("full image", display_img)
                cv2.moveWindow("full image", xpos, ypos)
                hwnd = win32gui.FindWindow(None, "full image")
                if hwnd > 0:
                    active = win32gui.GetForegroundWindow()
                    if active != hwnd:
                      [left,top,right,bottom] = win32gui.GetWindowRect(hwnd)
                      win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                                            left,top, right-left,
                                            bottom-top, 0)
                key_press = cv2.waitKey(20)
                if key_press == 27 or self.terminate:
                    #pub.sendMessage("SwitchInput", msg="closing")
                    #self.Close()
                    break
            else:
                break
                #this means no camera was found, I will send an error
                #message in this case in the eventual user friendly
                #version of the system
        pub.sendMessage("SwitchInput", msg="ready to close")

    def SearchImageFromRect(self, img, gray, rects):
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
                          (pos[0]+big_width, pos[1]+big_height), (0,255,0), 2)
            search_image = gray[pos[1]:pos[1]+big_height,
                                pos[0]:pos[0]+big_width]
        return (search_image, pos)

    def EyesFromFace(self, face_rect):
        [x, y, width, height] = face_rect
        eyes_top = y + int(height * 0.294)
        eyes_bottom = int(math.ceil(height * 0.221))
        return [[x - 10, eyes_top - 10, width + 10, eyes_bottom + 10]]

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
            if self.test:
                self.close_vals.append(max_shut_val)
                self.open_vals.append(max_open_val)
            if(max_shut_val - self.blink_correction > max_open_val and
               max_shut_val > self.blink_threshold):
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
        cv2.rectangle(img, blink_pos, blink_bottom_right, (255,0,0), 2)
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
        if self.test:
            print 'open'
            print self.open_vals
            print 'closed'
            print self.close_vals
        cv2.destroyAllWindows()
        self.cam.release()



if __name__ == "__main__":
  
    def listener1(msg): print "message received", msg
    pub.subscribe(listener1, 'SwitchInput')

    def listener2(msg): print "Error:- ", msg
    pub.subscribe(listener2, 'Error Message')

    tester = BlinkDetector((800,800), True, 'face')
    tester.RunDetect()
    tester.Close()
    

