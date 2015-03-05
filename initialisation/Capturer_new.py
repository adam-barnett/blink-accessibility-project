import cv2
import numpy as np
from wx.lib.pubsub import pub

"""
The opencv functions used during the initialisation to capture the base images
of the eyes.  Also finds the angle of the face to use in the capture
"""

"""
to do:
- fix all of the function names
"""


class box():
    def __init__(self, rect):
        if len(rect) == 4:
            self.l = rect[0]
            self.r = rect[0] + rect[2] 
            self.t = rect[1]
            self.b = rect[1] + rect[3]

    def __str__(self):
        out = ("t-" + str(self.t) + " b-" + str(self.b) + " l-" + str(self.l)
               + " r-" + str(self.r))
        return out

    def centre(self):
        return ((self.l+self.r)/2, (self.t+self.b)/2)

    def combine(self, box):
        if self.t > box.t:
            self.t = box.t
        if self.b < box.b:
            self.b = box.b
        if self.l > box.l:
            self.l = box.l
        if self.r < box.r:
            self.r = box.r

    def expand(self, expand_x, expand_y):
        x = int((self.r - self.l)*expand_x)
        y = int((self.b - self.t)*expand_y)
        self.b += y
        self.l -= x
        self.r += x

    def ImageSection(self, image, offset=None):
        if offset is not None:
            x = offset.l
            y = offset.t
        else:
            x = 0
            y = 0
        return image[self.t+y:self.b+y, self.l+x:self.r+x]
        

class Capturer():

    def __init__(self, screen_width=100):
        self.xpos = screen_width/2
        video_src = 0
        self.cam = cv2.VideoCapture(video_src)  
        self.face_cascade = cv2.CascadeClassifier('face.xml')
        self.xpos = screen_width/2
        self.find_rotation = False
        self.capture_eyes = False
        self.terminate = False
        self.diff_eyes_left = []
        self.diff_eyes_right = []
        self.face_box = None
        self.left_eye_box = None
        self.right_eye_box = None
        self.prev_img = None
        self.angle = 0.0


    def display(self):
        iter_since_diff = 0
        while True:
            ret, img = self.cam.read()
            if ret:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                if self.find_rotation:
                    face = self.rotation(gray)
                    if len(face) == 4:
                        self.face_box = box(face)
                        self.find_rotation = False
                        self.prev_img = self.face_box.ImageSection(
                            self.rotate_image(gray, self.angle))
                        pub.sendMessage("InitMsg", msg="rotation found")
                    else:
                        pass
                        #send message that rotation could not be found
                elif self.capture_eyes:
                    if self.prev_img is None or self.face_box is None:
                        pass
                        #this should not happen, need to deal with this
                        #appropriately
                    else:
                        cur_img = self.face_box.ImageSection(
                            self.rotate_image(gray, self.angle))
                        boxes = self.find_diffs(self.prev_img, cur_img)
                        eyes = self.DetectEyes(boxes,
                                            self.face_box.r - self.face_box.l,
                                            self.face_box.b - self.face_box.t)
##                        for eye in eyes:
##                            cv2.rectangle(gray, (eye.l + self.face_box.l,
##                                                 eye.t + self.face_box.t),
##                                          (eye.r + self.face_box.l,
##                                           eye.b + self.face_box.t),
##                                          (255,0,0), 2)
                        if len(eyes) == 2:
                            self.store_eyes(eyes, gray)
                            cv2.imshow('diff', self.diff_eyes_left[0])
                        elif len(eyes) == 0:
                            if len(self.diff_eyes_left) > 0:
                                if iter_since_diff > 10:
                                    cv2.imshow('open', gray)
                                    (l_closed, l_open) = \
                                             self.FindEyes(gray,
                                                            self.left_eye_box,
                                                            self.diff_eyes_left)
                                    (r_closed, r_open) = \
                                             self.FindEyes(gray,
                                                        self.right_eye_box,
                                                        self.diff_eyes_right)
                                    cv2.imwrite('left_open.png', l_open)
                                    cv2.imwrite('right_open.png', r_open)
                                    cv2.imwrite('right_closed.png', r_closed)
                                    cv2.imwrite('left_closed.png', l_closed)
                                    print 'eyes saved'
                                    self.capture_eyes = False
                                else:
                                    iter_since_diff += 1
                        self.prev_img = cur_img
                if self.left_eye_box is not None:
                    cv2.rectangle(gray, (self.left_eye_box.l + self.face_box.l,
                                         self.left_eye_box.t + self.face_box.t),
                                  (self.left_eye_box.r + self.face_box.l,
                                   self.left_eye_box.b + self.face_box.t),
                                  (255,0,0), 2)
                cv2.imshow('current_detection', gray)
                cv2.imshow('sub_img', self.face_box.ImageSection(gray))
                cv2.moveWindow('current_detection', self.xpos, 0)
                key_press = cv2.waitKey(50)
                if key_press == 27 or self.terminate:
                    break
        pub.sendMessage("InitMsg", msg="ready to close")

    def FindEyes(self, img, eye_box, eyes_list):
        method = eval('cv2.TM_CCOEFF_NORMED')
        search_img = eye_box.ImageSection(img, self.face_box)
##        img[eye_box.t + self.face_box.t:
##                         eye_box.b + self.face_box.t,
##                         eye_box.l + self.face_box.l:
##                         eye_box.r + self.face_box.l]
        furthest = None
        furthest_diff = 1.0
        for diff_img in eyes_list:
            cv2.imshow('diff', diff_img)
            comparison = cv2.matchTemplate(search_img,diff_img,method)
            _, max_val, _, max_loc = cv2.minMaxLoc(comparison)
            if max_val < furthest_diff:
                furthest_diff = max_val
                furthest = diff_img
        return (furthest, search_img)

    def find_diffs(self, prev_img, cur_img):
        diff_image = prev_img.copy()
        cv2.absdiff(prev_img, cur_img, diff_image)
        cv2.imshow('diff', diff_image)
        ret, disp = cv2.threshold(diff_image, 10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5),np.uint8)
        erosion = cv2.erode(disp,kernel,iterations = 2)
        dilation = cv2.dilate(erosion,kernel,iterations = 2)
        cv2.imshow('final', dilation)
        contours, hierarchy = cv2.findContours(dilation.copy(),
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for contour in contours:
            t = 10000
            l = 10000
            b = 0
            r = 0
            for point in contour:
                [x,y] = point[0]
                if x > r:
                    r = x
                if x < l:
                    l = x
                if y > b:
                    b = y
                if y < t:
                    t = y
            boxes.append(box([l,t,r-l,b-t]))
        return boxes

    def store_eyes(self, eyes, img):
        for eye in eyes:
            eye.expand(0.4, 0.3)
        self.diff_eyes_left.append(eyes[0].ImageSection(img,
                                                        self.face_box).copy())
##            img[eyes[0].t + self.face_box.t:
##                                       eyes[0].b + self.face_box.t,
##                                       eyes[0].l + self.face_box.l:
##                                       eyes[0].r + self.face_box.l].copy())
        if self.left_eye_box is None:
            self.left_eye_box = eyes[0]
        else:
            self.left_eye_box.combine(eyes[0])
        self.diff_eyes_right.append(eyes[1].ImageSection(img,
                                                        self.face_box).copy())
##            img[eyes[1].t + self.face_box.t:
##                                        eyes[1].b + self.face_box.t,
##                                        eyes[1].l + self.face_box.l:
##                                        eyes[1].r + self.face_box.l].copy())
        if self.right_eye_box is None:
            self.right_eye_box = eyes[1]
        else:
            self.right_eye_box.combine(eyes[1])
        

    def DetectEyes(self, rects, width, height):
        if len(rects) < 2 or len(rects) > 5:
            return []
        for box1 in rects:
            for box2 in rects:
                (x1,y1) = box1.centre()
                (x2,y2) = box2.centre()
                if  abs(x1-x2) > width / 3 and abs(y1-y2) < height / 10:
                    print 'found'
                    if box1.l > box2.r:
                        return [box2, box1]
                    else:
                        return [box1, box2]
        return []

    def rotation(self, img):
        angles = [0,2,-2,5,-5 ,10,-10]#, 15, -15, 20, -20, 25, -25, 30, -30, 35,
                  #-35, 40, -40, 45, -45, 50, -50, 55, -55, 60, -60, 65, -65, 70,
                  #-70, 75, -75, 80,  -80, 85, -85, 90, -90, 95, -95, 100, -100,
                  #105, -105, 110, -110]
        biggest_size = 0
        biggest_angle = None
        biggest_face = []
        for angle in angles:
            print 'trying angle: ', angle
            rot = self.rotate_image(img, angle)
            rects = self.face_cascade.detectMultiScale(rot, 1.10, 8,
                                    flags=cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
            if len(rects) > 0:
                [x, y, width, height] = rects[0]
                size = width * height
                if size > biggest_size:
                    biggest_angle = angle
                    biggest_size = size
                    biggest_face = rects[0]
        self.angle = biggest_angle
        print biggest_angle
        return biggest_face

    def rotate_image(self, image, angle):
        if angle == 0: return image
        height, width = image.shape[:2]
        rot_mat = cv2.getRotationMatrix2D((width/2, height/2), angle, 0.9)
        result = cv2.warpAffine(image, rot_mat, (width, height),
                                flags=cv2.INTER_LINEAR)
        return result

    def CloseCapt(self):
        self.terminate = True
        cv2.destroyAllWindows()
        self.cam.release()

if __name__ == "__main__":

    tester = Capturer(500)

    def InitMsg(msg):
        if msg == "rotation found":
            tester.capture_eyes = True
  
    pub.subscribe(InitMsg, ("InitMsg"))

    tester.find_rotation = True
    tester.display()
    tester.CloseCapt()
