import cv2
import math
import wx
import time


class InitEyeCapture(wx.Frame):
    
    def __init__(self, source):
        video_src = source
        self.iterations = 10
        self.introduction_text = ("This Procedure will initialise the system."
            "During it images of your closed and open eyes will be captured."
            "This will allow the system to detect when you are blinking."
            "Please try to stay still, the process will start in ")
        self.cam = cv2.VideoCapture(video_src)     
        self.eye_cascade = cv2.CascadeClassifier('eyes.xml')
        self.face_cascade =cv2.CascadeClassifier('face.xml')
        (screen_width, screen_height) = wx.DisplaySize()
        wx.Frame.__init__(self, None, 1, "title",
                          pos=(50,(screen_height*2)/3),
                          size=(screen_width-100, screen_height/4),
                          style=wx.NO_BORDER|
                          wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, size=self.GetSize())
        self.SetTransparent(220)
        font = wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL)
        self.text = wx.StaticText(self.panel, -1, "Hello World",
                                  style=wx.ALIGN_CENTRE, size=self.GetSize())
        self.text.SetFont(font)
        self.text_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ChangeText, self.text_timer)
        self.current_time = 0
        self.current_text = ""
        self.Show(False)

    def ChangeText(self, event):
        self.text.SetLabel(self.current_text + str(self.current_time))
        self.text.Wrap(self.GetSize()[0])
        self.current_time -= 1
        if self.current_time == -1:
            self.text_timer.Stop()
        

    def CaptureProcedure(self):
        self.Show(True)
        self.current_text = self.introduction_text
        self.current_time = 10
        self.text_timer.Start(1000)
        cascade = self.FindCaptureMethod()
        if cascade == self.eye_cascade:
            print 'eyes'
        elif cascade == self.face_cascade:
            print 'face'
        elif cascade is None:
            print 'uh oh'
        print 'done'
        """
        display message explaining entire process using wx.StaticText
            during this time decide on the capture method:
                eyes cascade
                face cascade
                or one of them with a rotated image
        display message saying "for the next 10 seconds face the screen and
        do not blink"
            capture based on match over time
            compare all images from match over time to find the one which
                isn't too different from the others
            get the eye image from that
        display message saying "for the next 10 seconds (until you hear a beep)
        shut your eyes gently"
            capture based on match over time
            compare all images from match over time to find the one which
                isn't too different from the others
            get the eye image from that
        display both sets of eyes
        save both sets of eyes
        """

    def FindSuitableMatch(self, matches):
        #compares matches to find one which isn't too different from the others
        #and returns that
        return matches[0]

    def FindCaptureMethod(self):
        found_eyes = self.MatchOverTime(self.iterations, self.eye_cascade)
        if len(found_eyes) > self.iterations / 0.8:
            return self.eye_cascade
        found_faces = self.MatchOverTime(self.iterations, self.face_cascade)
        if len(found_faces) > self.iterations / 0.8:
            return self.face_cascade
        #Eventually here we will follow up by checking different rotations
        #of the face for a particular case.  It will then also need to return
        #the rotation value and that will have to be set throughout the rest of
        #the class functions
        return None
        

    def EyesFromFace(self, face):
        (height, width) = face.shape
        eyes_top = int(height * 0.294)
        eyes_bottom = int(math.ceil(height * 0.515))
        eye_img = face[eyes_top:eyes_bottom, 0:width]
        return eye_img
        
        

    def MatchOverTime(self, iterations, cascade):
        matches = []
        while iterations > 0:
            ret, img = self.cam.read()
            if ret:
                print 'here'
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                rects = cascade.detectMultiScale(gray, 1.10, 8,
                                flags=cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
                if len(rects) > 0:
                    print 'here too'
                    [x, y, width, height] = rects[0]
                    cv2.rectangle(img, (x, y), (x+width, y+height),
                                  (255,0,0), 2)
                    cv2.imshow('current_detection', img)
                    captured = img[y:y+height, x:x+width]
                    matches.append(captured)
            iterations -= 1
        return matches

    def CloseInit(self):
        cv2.destroyAllWindows()
        self.cam.release()
        self.Close()
        self.Show(False)


if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.init = InitEyeCapture(0)
            self.init.CaptureProcedure()
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.init.CloseInit()
                self.ExitMainLoop()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
