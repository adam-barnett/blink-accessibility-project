import cv2
import winsound
import os
from wx.lib.pubsub import pub
import win32gui, win32con
import math
from utils.ImageUtilities import resize, rotate, ImageStore


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
    def __init__(self, (screen_width, screen_height)):
        if not (os.path.isfile('left_open.png')
                and os.path.isfile('left_closed.png')
                and os.path.isfile('right_open.png')
                and os.path.isfile('right_closed.png')
                and os.path.isfile('nose.png')
                and os.path.isfile('face.xml')
                and os.path.isfile('capture_info.txt')):
            msg = ('Basic file needed missing, please check folder for'
                   'the images (nose.png, left_closed.png, left_open.png'
                   'right_closed.png, right_open.png')
            pub.sendMessage('Error Message', msg=msg)
            self.init = False
            pub.sendMessage("SwitchInput", msg="closing")
        else:   
            self.error_correction = 0.015
            self.match_threshold = 0.7
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.eyes_open_msg_sent = True
            
            video_src = 0
            self.cam = cv2.VideoCapture(video_src)
            self.COMP_METHOD = 'cv2.TM_CCOEFF_NORMED'
            self.face_cascade = cv2.CascadeClassifier('face.xml')
            self.left = ImageStore(cv2.imread('left_open.png', 0),
                                   cv2.imread('left_closed.png', 0))
            self.right = ImageStore(cv2.imread('right_open.png', 0),
                                    cv2.imread('right_open.png', 0))
            self.nose = ImageStore(cv2.imread('nose.png', 0))

            expected_info = ['scale', 'rotation', 'nose_pos']
            info = open('capture_info.txt', 'r')
            for line in info:
                if line.startswith('scale'):
                    self.scale = int(line.split(':')[1])
                    expected_info.remove('scale')
                elif line.startswith('rotation'):
                    self.rotation = int(line.split(':')[1])
                    expected_info.remove('rotation')
                elif line.startswith('nose_pos'):
                    str_pos = line.split(':')[1].split(',')
                    self.nose.SetArea([int(i) for i in str_pos])
                    self.nose.ExpandArea(0.2)
                    expected_info.remove('nose_pos')
            if len(expected_info) != 0:
                print 'some values missing from capture_info.txt'
                print 'expected to see:'
                for line in expected_info: print line + ' ,'
                pub.sendMessage('Error Message', msg=msg)
                self.init = False
                pub.sendMessage("SwitchInput", msg="closing")
            
            self.terminate = True
            self.eyes_open_msg_sent = True
            self.init = True

    def RunDetect(self):
        self.terminate = False
        cv2.imshow("needed for focus", self.nose.norm)
        #cv2.resizeWindow("needed for focus", 20, 20)
        #cv2.moveWindow("needed for focus", -100, -100)
        if not self.init:
            return False
        while True:
            ret, img = self.cam.read()
            if ret:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                if(self.SetRotation(gray) is False):
                    #unable to find the rotation near the current nose position
                    if(self.SetRotation(gray) is False):
                        #unable to find nose in the entire image
                        #should count these occurences and if there are a
                        #bunch in a row then let the blinkcontroller know
                        #that no face is present
                        continue
                self.SetEyeRegions()
                cur_img = rotate(gray, self.rotation)
                if(self.CheckForBlink(cur_img)):
                    cv2.rectangle(cur_img, (self.left.l, self.left.t),
                              (self.left.r, self.left.b), (0,0,0), 2)
                    cv2.rectangle(cur_img, (self.right.l, self.right.t),
                              (self.right.r, self.right.b), (0,0,0), 2)
                    winsound.Beep(2500, 50)
                    self.eyes_open_msg_sent = False
                    pub.sendMessage("SwitchInput", msg="shut")
                else:
                    if not self.eyes_open_msg_sent:
                        #inform that the eyes are open again
                        self.eyes_open_msg_sent = True
                        pub.sendMessage("SwitchInput", msg="open")
                    if(self.left.l is not None):
                        #then check for scale here
                        pass
                
                
                xpos = self.screen_width - int(cur_img.shape[0]*1.5)
                ypos = self.screen_height/3  - cur_img.shape[1]/2
                cv2.imshow("full image", cur_img)
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
                    break
            else:
                break
                #this means no camera was found, I will send an error
                #message in this case in the eventual user friendly
                #version of the system
        pub.sendMessage("SwitchInput", msg="ready to close")

    def SetRotation(self, image):
        angles = [5, 0, -5]
        angles = [i + self.rotation for i in angles]
        self.nose.ExpandArea(0.4)
        max_val = 0.75
        max_ang =  None
        max_loc = (0,0)
        for angle in angles:
            rot = rotate(image, angle)
            nose_region = self.nose.ImageSection(rot)
            matches = cv2.matchTemplate(nose_region, self.nose.norm,
                                        cv2.TM_CCOEFF_NORMED)
            _, val, _, loc = cv2.minMaxLoc(matches)
            if val > max_val:
                max_val = val
                max_loc = loc
                max_ang = angle
        if max_ang is None:
            self.nose.SetAreaFromImage(image)
            return False
        prev_area = self.nose.GetArea()
        self.nose.SetAreaOffset(max_loc, self.nose.norm.shape, prev_area)
        self.rotation = max_ang
        return True

    def SetEyeRegions(self):
        expand = 0.3
        width = self.nose.r - self.nose.l
        left_shape = self.left.norm.shape[:2]
        l_top = int(self.nose.t - left_shape[0]*0.5 - width*expand)
        l_bot = int(self.nose.t + left_shape[0]*0.5 + width*expand)
        l_left = int(self.nose.l - left_shape[1] - width*expand)
        l_right = int(self.nose.l + width*expand)
        self.left.SetArea([l_left, l_top, l_right, l_bot])
        right_shape = self.right.norm.shape[:2]
        r_top = int(self.nose.t - right_shape[0]*0.5 - width*expand)
        r_bot = int(self.nose.t + right_shape[0]*0.5 + width*expand)
        r_left = int(self.nose.r - width*expand)
        r_right = int(self.nose.r + right_shape[1] + width*expand)
        self.right.SetArea([r_left, r_top, r_right, r_bot])

    def CheckForBlink(self, cur_img):
        left_img = self.left.ImageSection(cur_img)
        l_blink_val, _ = self.Match(left_img, self.left.special)
        l_open_val, l_open_loc = self.Match(left_img, self.left.norm)
        right_img = self.right.ImageSection(cur_img)
        r_blink_val, _ = self.Match(right_img, self.right.special)
        r_open_val, r_open_loc = self.Match(right_img, self.right.norm)
        if(l_blink_val + r_blink_val - self.error_correction*2 >
           l_open_val + r_open_val and l_blink_val > self.match_threshold
           and r_blink_val > self.match_threshold):
                #blinks matched better than open eyes and were above a threshold
                return True
        elif(l_open_val > self.match_threshold and
             r_open_val > self.match_threshold):
                #open eyes were found
                left_area = self.left.GetArea()
                self.left.SetAreaOffset(l_open_loc,
                                        self.left.norm.shape,
                                        left_area)
                right_area = self.right.GetArea()
                self.right.SetAreaOffset(r_open_loc,
                                         self.right.norm.shape,
                                         right_area)
        else:
            #no good match was found
            self.left.SetArea(None)
            self.right.SetArea(None)
        return False     

    def Match(self, big_img, small_img):
        matches = cv2.matchTemplate(big_img, small_img, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(matches)
        return val, loc

    def Close(self):
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
    

