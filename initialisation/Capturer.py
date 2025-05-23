import cv2
import numpy as np
from wx.lib.pubsub import pub
from Box import Box
import time

"""
The opencv functions used during the initialisation to capture the base images
of the eyes.  Also finds the angle of the face to use in the capture
"""     

class Capturer():

    def __init__(self, screen_width=100):
        self.xpos = screen_width/2
        video_src = 0
        self.cam = cv2.VideoCapture(video_src)  
        self.face_cascade = cv2.CascadeClassifier('face.xml')
        self.xpos = screen_width/2
        self.find_rotation = False
        self.capture_eyes_count = -1
        self.terminate = False
        self.diff_eyes_left = []
        self.diff_eyes_right = []
        self.face_box = None
        self.left_eye_box = None
        self.right_eye_box = None
        self.nose_box = None
        self.prev_img = None
        self.erosion_iterations = 2
        self.angle = 0.0


    def Display(self):
        time_of_diff = None
        while True and not self.terminate:
            ret, img = self.cam.read()
            if ret:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                if self.find_rotation:
                    face = self.FindRotation(gray)
                    if len(face) == 4:
                        self.face_box = Box(face)
                        self.find_rotation = False
                        self.prev_img = self.face_box.ImageSection(
                            self.RotateImage(gray, self.angle))
                        pub.sendMessage("InitMsg", msg="rotation found")
                    else:
                        pub.sendMessage("InitMsg", msg="no rotation found")
                elif self.capture_eyes_count >= 0:
                    if self.face_box is None:
                        self.capture_eyes_count = -1
                        pub.sendMessage("InitMsg", msg="no rotation found")
                    elif self.prev_img is None:
                        self.prev_img = self.face_box.ImageSection(
                            self.RotateImage(gray, self.angle))
                    else:
                        cur_img = self.face_box.ImageSection(
                            self.RotateImage(gray, self.angle))
                        boxes = self.FindDiffs(self.prev_img, cur_img)
                        eyes = self.DetectEyes(boxes,
                                            self.face_box.r - self.face_box.l,
                                            self.face_box.b - self.face_box.t)
                        if len(eyes) == 2:
                            self.StoreEyes(eyes, cur_img)
                            time_of_diff = time.time()
                        elif len(eyes) == 0:
                            if len(self.diff_eyes_left) > 0:
                                if time.time() - time_of_diff > 0.500:
                                    cv2.imshow('open', cur_img)
                                    self.SaveImages(cur_img)
                                    self.capture_eyes_count = -2
                                    pub.sendMessage("InitMsg",
                                                    msg="eyes saved")
                        self.prev_img = cur_img
                    self.capture_eyes_count += 1
                    if self.capture_eyes_count > 250:
                        pub.sendMessage("InitMsg", msg="no blink detected")
                gray = self.RotateImage(gray, self.angle)
                if self.left_eye_box is not None:
                    disp = gray.copy()
                    cv2.rectangle(disp, (self.left_eye_box.l + self.face_box.l,
                                         self.left_eye_box.t + self.face_box.t),
                                  (self.left_eye_box.r + self.face_box.l,
                                   self.left_eye_box.b + self.face_box.t),
                                  (255,0,0), 2)
                    cv2.rectangle(disp, (self.right_eye_box.l + self.face_box.l,
                                         self.right_eye_box.t + self.face_box.t),
                                  (self.right_eye_box.r + self.face_box.l,
                                   self.right_eye_box.b + self.face_box.t),
                                  (255,0,0), 2)
                    cv2.rectangle(disp, (self.face_box.l,self.face_box.t),
                                  (self.face_box.r,self.face_box.b),
                                  (0,0,255), 2)
                    cv2.imshow('areas', disp)
                cv2.imshow('current_detection', gray)
                cv2.moveWindow('current_detection', self.xpos, 0)
                key_press = cv2.waitKey(50)
                if key_press == 27 or self.terminate:
                    break
            else:
                pub.sendMessage("InitMsg", msg="no camera")
        pub.sendMessage("InitMsg", msg="ready to close")

    def ReturnSetUpVals(self):
        values = []
        values.append("rotation:" + str(self.angle) + "\n")
        scale = self.right_eye_box.l - self.left_eye_box.r
        values.append("scale:" + str(scale) + "\n")
        nose_pos = ','.join([str(self.nose_box.l + self.face_box.l),
                             str(self.nose_box.t + self.face_box.t),
                             str(self.nose_box.r + self.face_box.l),
                             str(self.nose_box.b + self.face_box.t)])
        values.append("nose_pos:" + nose_pos + "\n")
        return values
                                    

    def SaveImages(self, img):
        (l_closed, l_open) = self.FindEyes(img, self.left_eye_box,
                                           self.diff_eyes_left)
        (r_closed, r_open) = self.FindEyes(img, self.right_eye_box,
                                           self.diff_eyes_right)
        nose = self.FindNose(img, self.left_eye_box, self.right_eye_box)
        cv2.imwrite('left_open.png', l_open)
        cv2.imwrite('left_closed.png', l_closed)
        cv2.imwrite('right_open.png', r_open)
        cv2.imwrite('right_closed.png', r_closed)
        cv2.imwrite('nose.png', nose)

    def FindEyes(self, img, eye_box, eyes_list):
        method = eval('cv2.TM_CCOEFF_NORMED')
        search_img = eye_box.ImageSection(img)
        furthest = None
        furthest_diff = 1.0
        for diff_img in eyes_list:
            cv2.imshow('diff', diff_img)
            comparison = cv2.matchTemplate(search_img,diff_img,method)
            _, max_val, _, _ = cv2.minMaxLoc(comparison)
            if max_val < furthest_diff:
                furthest_diff = max_val
                furthest = diff_img
        return (furthest, search_img)

    def FindNose(self, img, left_eye, right_eye):
        l = left_eye.r
        r = right_eye.l
        t = int((left_eye.Centre()[1] + right_eye.Centre()[1])/2)
        b = t + int((r - l)*1.2)
        self.nose_box = Box([l,t,r-l,b-t])
        return self.nose_box.ImageSection(img).copy()
        
    def FindDiffs(self, prev_img, cur_img):
        diff_image = prev_img.copy()
        cv2.absdiff(prev_img, cur_img, diff_image)
        cv2.imshow('diff', diff_image)
        ret, disp = cv2.threshold(diff_image, 8, 255, cv2.THRESH_BINARY)
        cv2.imshow('after thresholding', disp)
        kernel = np.ones((5,5),np.uint8)
        erosion = cv2.erode(disp,kernel,iterations = self.erosion_iterations)
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
            boxes.append(Box([l,t,r-l,b-t]))
        return boxes

    def StoreEyes(self, eyes, img):
        for eye in eyes:
            eye.Expand(0.45, 0.5)
        if self.left_eye_box is None:
            self.left_eye_box = eyes[0]
        else:
            self.left_eye_box.Combine(eyes[0])
        self.diff_eyes_left.append(eyes[0].ImageSection(img).copy())
        if self.right_eye_box is None:
            self.right_eye_box = eyes[1]
        else:
            self.right_eye_box.Combine(eyes[1])
        self.diff_eyes_right.append(eyes[1].ImageSection(img).copy())
        
    def DetectEyes(self, rects, width, height):
        if len(rects) < 2 or len(rects) > 5:
            return []
        for box1 in rects:
            for box2 in rects:
                (x1,y1) = box1.Centre()
                (x2,y2) = box2.Centre()
                if  abs(x1-x2) > width / 3 and abs(y1-y2) < height / 10:
                    if box1.l > box2.r:
                        return [box2, box1]
                    else:
                        return [box1, box2]
        return []

    def FindRotation(self, img):
        small_angles = [-10, 0, 10]
        bigger_angles = [-115, -110, -105, -100, -95, -90, -85, -80, -75, -70,
                         -65, -60, -55, -50, -45, -40, -35, -30, -25, -20,
                         -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45,
                         50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105,
                         110, 115]
        longest_section = []
        #a quick check to see if the face is upright, as this is most likely
        for angle in small_angles:
            rot = self.RotateImage(img, angle)
            rects = self.face_cascade.detectMultiScale(rot, 1.10, 8,
                                    flags=cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
            if len(rects) > 0:
                longest_section.append(angle)
        if len(longest_section) != 3:
            longest_section = []
            current_section = []
            for angle in bigger_angles:
                rot = self.RotateImage(img, angle)
                rects = self.face_cascade.detectMultiScale(rot, 1.10, 8,
                                    flags=cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
                if len(rects) > 0:
                    current_section.append(angle)
                else:
                    if len(current_section) > len(longest_section):
                        longest_section = current_section
                    current_section = []
        face_rect = []
        if len(longest_section) != 0:
            best_angle = int(sum(longest_section)/len(longest_section))
            rot = self.RotateImage(img, best_angle)
            face = self.face_cascade.detectMultiScale(rot,1.10, 8,
                            flags=cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
            if(len(face) == 1):
                face_rect = face[0]
                self.angle = best_angle
            else:
                print "failed to find face in region: "
                print longest_section
                print "with best angle of:"
                print best_angle
        return face_rect

    def RotateImage(self, image, angle):
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
            tester.capture_eyes_count = 0
  
    pub.subscribe(InitMsg, ("InitMsg"))

    tester.find_rotation = True
    tester.Display()
    tester.CloseCapt()
