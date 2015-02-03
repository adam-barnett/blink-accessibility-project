import cv2
import time
import math
from wx.lib.pubsub import pub

class Capturer():

    def __init__(self, test=False, screen_width=100):
        print 'initialising capturer'
        video_src = 0
        self.cam = cv2.VideoCapture(video_src)  
        self.eye_cascade = cv2.CascadeClassifier('eyes.xml')
        self.face_cascade = cv2.CascadeClassifier('face.xml')
        self.cascades = {'eyes':self.eye_cascade, 'face':self.face_cascade}
        self.casc_iter = iter(self.cascades)
        self.set_capture_method = False
        self.capture_image = False
        self.xpos = screen_width/2
        self.terminate = False
        self.iterations = 0
        self.matches = []
        self.capture_cascade = None
        self.capture_rotation = 0.0


    def display(self):
        count = 0
        cascade = None
        matches = []
        #'wait' is used to keep 0.5 seconds between the captures.  if the
        #number of iterations need to be changed significantly then wait should
        #be tied to them (and likely yet another class variable would be needed)
        wait = time.time()
        while True:
            ret, img = self.cam.read()
            if ret:
                capture = None
                if self.set_capture_method and cascade == None:
                    #we are at the start of an iteration
                    try:
                        cascade = self.casc_iter.next()
                    except StopIteration:
                        matches = []
                        self.set_capture_method = False
                        count = 0
                        pub.sendMessage("InitMsg", msg="no_method_found")
                        #send message that the capture method finding is over
                        #but a method was not successfully found
                if self.capture_image and  cascade == None:
                        cascade = self.capture_cascade
                if cascade is not None and time.time() - wait > 0.5:
                    wait = time.time()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    rects = self.cascades[cascade].detectMultiScale(gray, 1.10,
                                8, flags=cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
                    if len(rects) > 0:
                        [x, y, width, height] = rects[0]
                        capture = img[y:y+height, x:x+width].copy()
                        cv2.rectangle(img, (x, y), (x+width, y+height),
                                      (255,0,0), 2)
                    if count == self.iterations:
                        if self.set_capture_method:
                            if len(matches) > self.iterations * 0.8:
                                self.capture_cascade = cascade
                                self.set_capture_method = False
                                pub.sendMessage("InitMsg", msg="method_found")
                        elif self.capture_image:
                            temp_save = self.FindSuitableMatch(matches)
                            cv2.imwrite('temp.png', temp_save)
                            self.capture_image = False
                            pub.sendMessage("InitMsg", msg="img_saved")
                        cascade = None
                        matches = []
                        count = 0
                    elif capture is not None:
                        if cascade == 'face':
                            matches.append(self.EyesFromFace(capture))
                        else:
                            matches.append(capture)
                    count += 1
                xpos = self.xpos - img.shape[0]/2
                cv2.imshow('current_detection', img)
                cv2.moveWindow('current_detection', xpos, 0)
                key_press = cv2.waitKey(50)
                if key_press == 27 or self.terminate:
                    pub.sendMessage("InitMsg", msg="closing")
                    cv2.destroyAllWindows()
                    self.CloseCapt()
                    break

    def EyesFromFace(self, face):
        (height, width) = face.shape[:2]
        eyes_top = int(height * 0.294)
        eyes_bottom = int(math.ceil(height * 0.515))
        eye_img = face[eyes_top:eyes_bottom, 0:width]
        return eye_img

    def FindSuitableMatch(self, matches):
        #compares matches to find one which isn't too different from the others
        #and returns that
        return matches[6]


    def CloseCapt(self):
        print 'capturer closing itself'
        cv2.destroyAllWindows()
        self.cam.release()
