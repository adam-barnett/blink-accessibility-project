import wx
import time
from wx.lib.pubsub import pub
from BlinkDetector import BlinkDetector
from mouse import MouseUI, MouseController
from initialisation import InitialisationControl


"""
A simple frame which will coordinate between the blink detection and display
elements to allow the user control
"""

class BlinkControllerFrame(wx.Frame):
    
    def __init__(self, moving_horizontally=True, speed=20):
        wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                          size=(0,0), style=
                          wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
        self.watcher = None
        self.mouse_ui = None
        self.mouse_cont = None
        pub.subscribe(self.SwitchInput, ("SwitchInput"))
        pub.subscribe(self.InitManager, ("InitToMain"))
        self.blink_started = None
        self.initialiser = InitialisationControl.InitialisationControl()

    def InitManager(self, msg):
        print msg + '- controller message'
        if msg == "initialisation_finished":
            if getattr(self, 'initialiser', None):
                print 'closing initialiser'
                self.initialiser.Close()
            self.mouse_ui = MouseUI.MouseUI()
            self.mouse_cont = MouseController.MouseController()
            def to_be_done():
                print 'currently there is no menu available'
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
            self.mouse_ui.Show(True)
            self.mouse_cont.Show()
            self.watcher = BlinkDetector(wx.DisplaySize(),False, False)
            self.watcher.RunDetect()
        elif msg == "failed_to_capture":
            #eventually a backup plan for this should be found
            #for now we just close
            self.CloseWindow()
        elif msg == "closing":
            self.CloseWindow()
        
    def SwitchInput(self, msg):
        if msg == "closing":
            #the blink detector is closing
            self.CloseWindow()
        elif msg == "shut":
            current_blink = time.time()
            if self.blink_started is None:
                self.blink_started = current_blink
            elif current_blink - self.blink_started > 0.150:
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
        print 'controller closing'
        if getattr(self, 'watcher', None):
            self.watcher.Close()
        if getattr(self, 'initialiser', None):
            self.initialiser.Close()
        if getattr(self, 'mouse_ui', None):
            print 'mouse_ui_close'
            self.mouse_ui.Close()
        if getattr(self, 'mouse_cont', None):
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
