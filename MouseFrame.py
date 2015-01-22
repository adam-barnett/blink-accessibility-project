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
        self.button_dict = {1:"up", 2:"down", 3:"left", 4:"right", 5:"scrl_down",
               6:"scrl_up", 7:"left_click", 8:"dbl_left_click", 9:"right_click"}
        button_size = (50,50)
        config = (5,2)
        (screen_w, screen_h) = wx.DisplaySize()
        this_size = (button_size[0]*config[0], button_size[1]*config[1])
        wx.Frame.__init__(self, None, 1, "title",
                          pos=(screen_w - this_size[0],
                               screen_h*3/4 - this_size[1]/2),
                          size=this_size,
                          style=wx.NO_BORDER|
                          wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, size=self.GetSize())
        self.SetTransparent(230)
        current_dir = os.getcwd() + "\\buttons\\"

        self.buttons = []
        self.highlight_images = []
        self.normal_images = []
        x = 0
        y = 0
        for i in xrange(10):
            button_f = current_dir + "button" + str(i) + ".bmp"
            highlight_f = current_dir + "highlight" + str(i) + ".bmp"
            clicked_f = current_dir + "clicked" + str(i) + ".bmp"
            butt_im = wx.Image(button_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            high_im = wx.Image(highlight_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            click_im = wx.Image(clicked_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            button = wx.BitmapButton(self.panel, id=-1, bitmap=butt_im,
                                     pos=(x*button_size[0], y*button_size[1]),
                                     size=button_size)
            self.buttons.append(button)
            self.highlight_images.append(high_im)
            self.normal_images.append(butt_im)
            if(x == config[0]-1):
                x = 0
                y += 1
            else:
                x += 1

        self.cur_high = 0
        self.buttons[0].SetBitmap(self.highlight_images[0])

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.IterateThroughButtons, self.timer)
        self.timer.Start(400)

    def ButtonClick(self, event):
        print 'button clicked'

    def IterateThroughButtons(self, event):
        self.buttons[self.cur_high].SetBitmap(self.normal_images[self.cur_high])
        self.cur_high = (self.cur_high + 1) % len(self.buttons)
        self.buttons[self.cur_high].SetBitmap(self.highlight_images[self.cur_high])

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
