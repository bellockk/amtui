import logging
import wx


class ArtifactTree(wx.TreeCtrl):

    def __init__(self, parent, *args, **kwargs):
        super(ArtifactTree, self).__init__(
            parent, *args, **kwargs)

        # Bind to Events
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnShowPopup)
        # self.Bind(wx.EVT_TREE_KEY_DOWN, self.OnKeyDown)

        # Key Bindings
        self.SetAcceleratorTable(wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, ord('J'), wx.ID_DOWN)]))

    def OnKeyDown(self, event):
        logging.debug(
            'Artifact Tree KeyPress Detected: KeyCode=%s Character=%s' % (
                event.GetKeyCode(), chr(event.GetKeyCode())))

        # Enable Vi movements
        if chr(event.GetKeyCode()).lower() == 'j':
            # TODO: Post a wx.ID_DOWN event
            pass

        # Allow other bindings to consume this event
        event.Skip()

    def OnShowPopup(self, event):
        self.popupmenu = wx.Menu()
        for text in ["Add", "Delete", "Edit"]:
            self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnSelectContext)
        self.PopupMenu(self.popupmenu, event.GetPoint())
        self.popupmenu.Destroy()

    def OnSelectContext(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetText()
        logging.info(text)
