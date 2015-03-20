import cv2

"""
A simple class for dealing with boxes around regions in images, used by
Capturer
"""

class Box():
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

    def Centre(self):
        return ((self.l+self.r)/2, (self.t+self.b)/2)

    def Combine(self, box):
        if self.t > box.t:
            self.t = box.t
        if self.b < box.b:
            self.b = box.b
        if self.l > box.l:
            self.l = box.l
        if self.r < box.r:
            self.r = box.r

    def Expand(self, expand_x, expand_y):
        x = int((self.r - self.l)*expand_x)
        y = int((self.b - self.t)*expand_y)
        self.t += int(0.5*y)
        self.b += 2*y
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
