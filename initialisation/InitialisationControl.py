import wx
from wx.lib.pubsub import pub
from Capturer import Capturer
from TextDisplay import TextDisplay
import os
import time
import winsound

"""
During the initialisation of the system this class coordinates the TextDisplay
and the Capturer in getting the correct images of the users eyes, then it
communicates with the main system and translates all of the captured systems
and information.
"""

class InitialisationControl():
    def __init__(self, test=False):
        self.capture = None
        self.failed = False
        self.blink_saved = False
        current_dir = os.getcwd()
        if not test:
            messages_file = current_dir + "\\initialisation\\init_messages.txt"
        else:
            messages_file = current_dir + "\\init_messages.txt"   
        txt = open(messages_file, 'r')
        self.messages = {}
        for line in txt:
            parts = line.split(":")
            self.messages[parts[0]] = parts[1]
        txt.close()
        self.capture_vals = open(current_dir + "\\capture_info.txt", 'w')
        self.capture_vals.truncate
        self.text_display = TextDisplay()
        self.text_display.Show(True)
        pub.subscribe(self.InitMsg, ("InitMsg"))
        self.text_display.DisplayMessage(self.messages["welcome"], 3)
        (width, _height) = wx.DisplaySize()
        self.capture = Capturer(screen_width=width)
        self.capture.Display()
        

    def InitMsg(self, msg):
        print msg
        if msg == "ready to close":
            if self.failed:
                self.text_display.DisplayMessage(
                    self.messages["no camera"], 5)
            else:
                self.Close()
        elif msg == "rotation found":
            while time.time() - self.rotation_pause < 4:
                pass
            self.text_display.DisplayMessage(self.messages["capture eyes"])
            self.capture.capture_eyes_count = 0
        elif msg == "eyes saved":
            self.text_display.DisplayMessage(self.messages["finished"])
            self.blink_saved = True
            self.capture.terminate = True
        elif msg == "no rotation found":
            self.text_display.DisplayMessage(self.messages["no rotation"], 30)
        elif msg == "no blink detected":
            self.text_display.DisplayMessage(self.messages["no blink"])
            self.capture.erosion_iterations = 1
            self.capture.capture_eyes_count = 0
        elif msg == "no camera":
            self.failed = True
            self.capture.terminate = True                                 
        elif msg == "text display done":
            if self.failed or self.capture is None:
                #the camera was not found so we close
                self.Close()
            else:
                #the welcome message is over or the rotation needs to be
                #searched for again (after the 'no rotation' message)
                self.text_display.DisplayMessage(
                    self.messages["find rotation"])
                self.rotation_pause = time.time()
                self.capture.find_rotation = True   

    def Close(self):
        self.text_display.CloseWindow()
        pub.unsubscribe(self.InitMsg, ("InitMsg"))
        output = self.capture.ReturnSetUpVals()
        for line in output:
            self.capture_vals.write(line)
        self.capture_vals.close()
        if getattr(self, 'capture', None):
            self.capture.CloseCapt()
        if self.blink_saved == True:
            pub.sendMessage("InitToMain", msg="initialisation_finished")
        else:
            pub.sendMessage("InitToMain", msg="failed_to_capture")



if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.init = InitialisationControl(True)
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.init.Close()
                self.ExitMainLoop()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
