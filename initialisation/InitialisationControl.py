import wx
from wx.lib.pubsub import pub
from Capturer import Capturer
from TextDisplay import TextDisplay
import os
import winsound

"""
During the initialisation of the system this class coordinates the TextDisplay
and the Capturer in getting the correct images of the users eyes, then it
communicates with the main system and translates all of the captured systems
and information.
"""

class InitialisationControl():
    def __init__(self, test=False):
        (width, _height) = wx.DisplaySize()
        self.capture = Capturer(screen_width=width)
        pub.subscribe(self.InitMsg, ("InitMsg"))
        self.capture.set_capture_method = False
        self.capture.iterations = 10
        self.blink_saved = False
        self.open_saved = False
        self.last_capture_msg = None
        self.text_finished = False
        self.fail_message = ("The system was not able to find eyes or a face"
                             "In the camera, check the camera and lighting"
                             "and try again")
        current_dir = os.getcwd()
        if not test:
            messages_file = current_dir + "\\initialisation\\init_messages.txt"
        else:
            messages_file = current_dir + "\\init_messages.txt"   
        self.messages = open(messages_file, 'r')
        self.capture_vals = open(current_dir + "\\capture_info.txt", 'w')
        self.capture_vals.truncate
        (msg, countdown, time) = self.GetMsg(self.messages)
        self.text_display = TextDisplay(msg)
        self.text_display.DisplayMessage(msg, countdown, time)
        self.text_display.Show(True)
        self.welcome_message = True
        self.capture.display()

    def InitMsg(self, msg):
        if msg == "closing" or self.last_capture_msg == "closing":
            self.Close()
        elif msg == "method_found" and self.text_finished:
            self.last_capture_msg = None
            self.text_finished = False
            self.capture.capture_image = True
            winsound.Beep(2500, 100)
            (msg, countdown, time) = self.GetMsg(self.messages)
            self.text_display.DisplayMessage(msg, countdown, time)
        elif msg == "no_method_found" and self.text_finished:
            self.text_finished = False
            self.capture.finished = True
            self.text_display.DisplayMessage(self.fail_message, -1, 5000)
            pub.sendMessage("InitToMain", msg="failed_to_capture")
            self.last_capture_msg = "closing"
        elif msg == "img_saved" and self.text_finished:
            self.last_capture_msg = None
            self.text_finished = False
            if not self.open_saved:
                if os.path.isfile("open.png"):
                    os.remove("open.png")
                os.rename("temp.png", "open.png")
                self.open_saved = True
                winsound.Beep(2500, 100)
                (msg, countdown, time) = self.GetMsg(self.messages)
                self.text_display.DisplayMessage(msg, countdown, time)
                self.capture.capture_image = True
            elif not self.blink_saved:
                if os.path.isfile("blink.png"):
                    os.remove("blink.png")
                os.rename("temp.png", "blink.png")
                winsound.Beep(2500, 100)
                (msg, countdown, time) = self.GetMsg(self.messages)
                self.text_display.DisplayMessage(msg, countdown, time)
                self.blink_saved = True
                #self.capture.finished = True
        elif msg == "text_display_finished":
            self.text_finished = True
            if self.welcome_message == True:
                winsound.Beep(2500, 100)
                (msg, countdown, time) = self.GetMsg(self.messages)
                self.text_display.DisplayMessage(msg, countdown, time)
                self.capture.set_capture_method = True
                self.welcome_message = False
                self.text_finished = False
            elif self.blink_saved == True:
                self.Close()                      
            elif self.last_capture_msg is not None:
                self.InitMsg(self.last_capture_msg)
        else:
            self.last_capture_msg = msg

    def GetMsg(self, input_file):
        try:
            msg = input_file.next()
            countdown = int(input_file.next())
            time = int(input_file.next())
            return (msg, countdown, time)
        except ValueError:
            print 'error, the init_messages.txt should take the form:'
            print 'msg - a string'
            print 'iterations - an int'
            print 'time = a time'
            print 'closing now'
            self.Close()
        except StopIteration:
            print 'error the init_messages.txt does not have enough lines'
            print 'it should have a number of lines divisible by 3'
            self.Close()

    def Close(self):
        self.text_display.CloseWindow()
        self.messages.close()
        pub.unsubscribe(self.InitMsg, ("InitMsg"))
        if self.capture.capture_cascade is not None:
            self.capture_vals.write('cascade: ' +
                                    self.capture.capture_cascade + '\n')
            self.capture_vals.write('rotation: ' +
                                    str(self.capture.capture_rotation) + '\n')
        self.capture_vals.close()
        if getattr(self, 'capture', None):
            self.capture.terminate = True
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
                self.init.CloseInit()
                self.ExitMainLoop()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
