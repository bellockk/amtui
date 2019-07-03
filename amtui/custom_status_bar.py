import wx


class CustomStatusBar(wx.StatusBar):

    def __init__(self, parent):
        super(CustomStatusBar, self).__init__(parent, -1)

        self.SetFieldsCount(2)

    def SetStatusText(self, status):
        status_size = wx.Window.GetTextExtent(self, status)[0]
        self.SetStatusWidths([-1, status_size + 30])
        super(CustomStatusBar, self).SetStatusText(status, 1)
