import wx
from wx.lib.pubsub import pub
from Capturer import Capturer
import os

class InitialisationControl():
    def __init__(self):
        self.capture = Capturer()
        pub.subscribe(self.InitMsg, ("InitMsg"))
        self.capture.set_capture_method = True
        self.capture.iterations = 10
        self.blink_saved = False
        self.open_saved = False
        #start the initial message text
        self.capture.display()

    def InitMsg(self, msg):
        print msg
        if msg == "closing":
            self.Close()
        elif msg == "method_found":
            self.capture.capture_image = True
            #start the open eyes capture text
        elif msg == "no_method_found":
            self.capture.finished = True
            #display a message to the user that initialisation was
            #unable to capture the eyes and old eyes must be used
        elif msg == "img_saved":
            if not self.open_saved:
                if os.path.isfile("open.png"):
                    os.remove("open.png")
                os.rename("temp.png", "open.png")
                self.open_saved = True
                #start the capture shut eyes capture text
                self.capture.capture_image = True
            elif not self.blink_saved:
                if os.path.isfile("blink.png"):
                    os.remove("blink.png")
                os.rename("temp.png", "blink.png")
                self.blink_saved = True
                self.capture.finished = True
            

    def Close(self):
        pass



if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.init = InitialisationControl()
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.init.CloseInit()
                self.ExitMainLoop()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
