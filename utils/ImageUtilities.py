import cv2

def resize(image, scale, interpol = cv2.INTER_AREA):
    if scale == 1.0:
        return image
    new_dim = (int(image.shape[1]*scale), int(image.shape[0]*scale))
    resized = cv2.resize(image, new_dim, interpolation = interpol)
    return resized

def rotate(image, angle):
    if angle == 0: return image
    height, width = image.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((width/2, height/2), angle, 0.9)
    result = cv2.warpAffine(image, rot_mat, (width, height),
                            flags=cv2.INTER_LINEAR)
    return result

class ImageStore():
    def __init__(self, norm, image2=None, area=None):
        self.norm = norm;#this should be the open eyes
        if image2 is not None:
            self.special = image2 #this is the closed eyes
        else:
            self.special = norm
        self.SetArea(area)

    def SetArea(self, area):
        #area should be of the form [l,t,r,b]
        if area is None or len(area) != 4:
            self.l = None
            self.t = None
            self.r = None
            self.b = None
        else:
            self.l = area[0]
            self.t = area[1]
            self.r = area[2]
            self.b = area[3]

    #shape is of the form (height, width)
    def SetAreaOffset(self, top, shape, offset=None):
        if offset is not None:
            xoff = offset[0]
            yoff = offset[1]
        else:
            xoff = 0
            yoff = 0
        self.l = top[0] + xoff
        self.r = top[0] + shape[1] + xoff
        self.t = top[1] + yoff
        self.b = top[1] + shape[0] + yoff
        
    def GetArea(self):
        return [self.l, self.t, self.r, self.b]

    def ExpandArea(self, expansion):
        x = int(((self.r-self.l)/2.0)*expansion)
        y = int(((self.b-self.t)/2.0)*expansion)
        self.l = self.l - x
        self.r = self.r + x
        self.t = self.t - x
        self.r = self.r + x

    def ImageSection(self, image, offset=None):
        if offset is not None:
            x = offset[0]
            y = offset[1]
        else:
            x = 0
            y = 0
        return image[self.t+y:self.b+y, self.l+x:self.r+x]
        
        
