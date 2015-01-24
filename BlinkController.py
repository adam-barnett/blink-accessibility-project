import wx
import time
from wx.lib.pubsub import pub
from BlinkDetector import BlinkDetector
from MouseUI import MouseUI
from MouseController import MouseController


"""
A simple frame which will coordinate between the blink detection and display
elements to allow the user control
"""

class BlinkControllerFrame(wx.Frame):
    
    def __init__(self, moving_horizontally=True, speed=20):
        def to_be_done():
            print 'currently there is no menu available'

        self.mouse_ui = MouseUI()
        self.mouse_ui.Show(True)
        self.mouse_cont = MouseController()
        self.mouse_actions = {"up":self.mouse_cont.Up,
                              "down":self.mouse_cont.Down,
                              "left":self.mouse_cont.Left,
                              "right":self.mouse_cont.Right,
                              "scrl_down":self.mouse_cont.ScrlDown,
                              "scrl_up":self.mouse_cont.ScrlUp,
                              "left_click":self.mouse_cont.LeftClick,
                              "dbl_left_click":self.mouse_cont.DoubleLeftClick,
                              "right_click":self.mouse_cont.RightClick,
                              "menu":to_be_done}

        wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                          size=(0,0), style=
                          wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
        self.watcher = BlinkDetector(wx.DisplaySize(),True)
        pub.subscribe(self.SwitchInput, ("SwitchInput"))
        self.blink_started = None
        self.watcher.RunDetect()
        
    def SwitchInput(self, msg):
        if msg == "closing":
            #close command sent
            self.CloseWindow()
        elif msg == "shut":
            current_blink = time.time()
            if self.blink_started is None:
                self.blink_started = current_blink
            elif current_blink - self.blink_started > 0.100:
                #blink detected
                self.blink_started = None
                command = self.mouse_ui.ClickInput()
                self.mouse_actions[command]()
                if command == "right_click":
                    #need to grab back the focus so that the timers all work
                    #(in case a menu was opened which stole it)
                    self.SetFocus()
        elif msg == "open":
            #eyes are open
            self.blink_started = None

    def CloseWindow(self):
        self.mouse_ui.Close()
        self.mouse_cont.Close()
        self.Destroy()


if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.frame = BlinkControllerFrame()
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame.CloseWindow()
                self.ExitMainLoop() 
      
    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
