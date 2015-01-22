import wx
import time
import os

"""
A simple frame which displays the options for controlling the mouse,
highlighting them in order until the a click is entered, returning the
highlighted button when it is.
"""

class MouseFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                  size=(50, 50), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
          
        self.panel = wx.Panel(self, size=self.GetSize())

        current_dir = os.getcwd()

        button_image_file = (current_dir +
                            "\\buttons\\button_up_no_highlight.bmp")
        button_image_pressed_file = (current_dir +
                                     "\\buttons\\button_up_clicked.bmp")
        button_image_hover_file = (current_dir +
                                   "\\buttons\\button_up_highlighted.bmp")
        self.button_main_image = wx.Image(button_image_file,
                                     wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.button_hover_image = wx.Image(button_image_hover_file,
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        button_select_image = wx.Image(button_image_pressed_file,
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.button  = wx.BitmapButton(self.panel, id=-1,
                                       bitmap=self.button_main_image,
                                       size=(self.button_main_image.GetWidth(),
                                             self.button_main_image.GetHeight()))
        self.button.SetBitmapHover(self.button_hover_image)
        self.button.SetBitmapSelected(button_select_image)
        self.button.Bind(wx.EVT_BUTTON, self.ButtonClick)
        self.button_norm = True

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.HighlightButton, self.timer)
        self.timer.Start(400)

    def ButtonClick(self, event):
        print 'button clicked'

    def HighlightButton(self, event):
        if self.button_norm:
            self.button.SetBitmap(self.button_hover_image)
            print 'switching to hover'
        else:
            self.button.SetBitmap(self.button_main_image)
            print 'switching back to main'
        self.button_norm = not self.button_norm

    def CloseWindow(self):
        self.Close()
        self.Show(False)




if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.frame = MouseFrame()  
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame.CloseWindow()
                self.ExitMainLoop()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
