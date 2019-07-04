import os
import sys
import traceback
import wx
import wx.aui
import wx.lib.newevent
import logging

__all__ = ['gui']
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])

from amt.load import load
sys.path.insert(0, dirName)
import images
from custom_status_bar import CustomStatusBar


def MyExceptionHook(etype, value, trace):
    """
    Handler for all unhandled exceptions.

    :param `etype`: the exception type (`SyntaxError`, `ZeroDivisionError`,
                    etc...);
    :type `etype`: `Exception`
    :param string `value`: the exception error message;
    :param string `trace`: the traceback header, if any (otherwise, it prints
    the standard Python header: ``Traceback (most recent call last)``.
    """
    tmp = traceback.format_exception(etype, value, trace)
    exception = "".join(tmp)
    logging.error(exception)


class wxLogHandler(logging.Handler):
    """
    A handler class which sends log strings to a wx object
    """
    wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()

    def __init__(self, wxDest=None):
        """
        Initialize the handler
        @param wxDest: the destination object to post the event to
        @type wxDest: wx.Window
        """
        logging.Handler.__init__(self)
        self.wxDest = wxDest
        self.level = logging.DEBUG

    def flush(self):
        """
        does nothing for this handler
        """
        pass

    def emit(self, record):
        """
        Emit a record.

        """
        try:
            msg = self.format(record)
            evt = self.wxLogEvent(message=msg, levelname=record.levelname)
            wx.PostEvent(self.wxDest, evt)
        except (KeyboardInterrupt, SystemExit):
            raise


class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='AMT',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # Install Error Hook
        sys.excepthook = MyExceptionHook

        # Create a logger for this class
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        handler = wxLogHandler(self)
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s][%(levelname)-8s] %(message)s"))
        # self.log.addHandler(handler)
        logger = logging.getLogger()
        logger.addHandler(handler)

        # Create Menu
        self.InitUI()

        self._mgr = wx.aui.AuiManager(self)

        # create several text controls
        self.image_list = wx.ImageList(16, 16, True, 2)
        self.folder_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
        self.file_list_image = self.image_list.Add(
            images.square_brackets.Image.Scale(16,16).ConvertToBitmap())
        self.file_dictionary_image = self.image_list.Add(
            images.curly_brackets.Image.Scale(16,16).ConvertToBitmap())
        self.list_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_LIST_VIEW, wx.ART_OTHER, wx.Size(16, 16)))
        self.dictionary_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_REPORT_VIEW, wx.ART_OTHER, wx.Size(16, 16)))
        self.record_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_EXECUTABLE_FILE, wx.ART_OTHER, wx.Size(16, 16)))
        self.tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.Size(160, 250),
                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        self.tree.AssignImageList(self.image_list)
        text2 = wx.TextCtrl(self, -1, '',
                            wx.DefaultPosition, wx.Size(200, 150),
                            wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY |
                            wx.HSCROLL)
        text2.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False,
                              u'Consolas'))

        text3 = wx.TextCtrl(self, -1, 'Main content window',
                            wx.DefaultPosition, wx.Size(200, 150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        self.logconsole = text2

        # add the panes to the manager
        self._mgr.AddPane(self.tree, wx.LEFT, 'Artifact Tree')
        self._mgr.AddPane(text2, wx.BOTTOM, 'Log Console')
        self._mgr.AddPane(text3, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        # Create Status Bar
        self.status_bar = CustomStatusBar(self)
        self.SetStatusBar(self.status_bar)
        self.status_bar.SetStatusText("Welcome to AMT")

        self.content_not_saved = False

        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(wxLogHandler.EVT_WX_LOG_EVENT, self.onLogEvent)

    def InitUI(self):

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        new_button = fileMenu.Append(
            wx.ID_NEW, '&New\tCtrl+N', 'Create a new session')
        open_file_button = fileMenu.Append(
            wx.ID_ANY, 'Open &File\tCtrl+F', 'Open a file')
        open_directory_button = fileMenu.Append(
            wx.ID_ANY, 'Open &Directory\tCtrl+D', 'Open a directory')
        self.save_button = fileMenu.Append(
            wx.ID_SAVE, '&Save\tCtrl+S', 'Save to current location')
        self.save_button.Enable(False)
        self.save_as_button = fileMenu.Append(
            wx.ID_SAVEAS, 'Save &As\tCtrl+A', 'Save to a new location')
        self.save_as_button.Enable(False)

        fileMenu.AppendSeparator()

        self.close_button = fileMenu.Append(wx.ID_CLOSE, "&Close\tCtrl+C",
                                            "Close current")
        self.close_button.Enable(False)
        quit_button = fileMenu.Append(
            wx.ID_EXIT, '&Quit\tCtrl+Q', 'Exit the application')

        # Bind Events
        self.Bind(wx.EVT_MENU, self.OnNew, new_button)
        self.Bind(wx.EVT_MENU, self.OnOpenFile, open_file_button)
        self.Bind(wx.EVT_MENU, self.OnOpenDirectory, open_directory_button)
        self.Bind(wx.EVT_MENU, self.OnSave, self.save_button)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, self.save_as_button)
        self.Bind(wx.EVT_MENU, self.OnClose, self.close_button)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_button)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

    def decorate_tree(self, node, branch):
        for key, value in branch.items():
            if key.startswith('_'):
                continue
            if isinstance(value, dict):
                if '__file__' in value:
                    # TODO: switch between file_list_image and
                    # file_dictionary_image
                    image = self.file_list_image
                else:
                    image = self.folder_image
                sub_node = self.tree.AppendItem(node, key, image)
                self.decorate_tree(sub_node, value)
            elif isinstance(value, (tuple, list, set)):
                sub_node = self.tree.AppendItem(node, key, self.list_image)
                # for item in value:
                #     self.decorate_tree(sub_node, value)
            else:
                sub_node = self.tree.AppendItem(
                    node, key, self.record_image)

    def OnNew(self, e):
        LOGGER.info("New")

    def OnOpenFile(self, e):
        LOGGER.info("Open File")
        if self.content_not_saved:
            if wx.MessageBox("Save current session?", "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        # otherwise ask the user what new file to open
        with wx.FileDialog(
                self, "Open Artifacts file",
                wildcard="AMT files (*.yaml)|*.yaml",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                logging.info("Load file: %s", pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot(os.path.basename(os.path.splitext(
            pathname)[0]), self.file_list_image)
        self.decorate_tree(root, load(pathname))
        self.tree.Expand(root)

    def OnOpenDirectory(self, e):
        LOGGER.info("Open Directory")
        if self.content_not_saved:
            if wx.MessageBox("Save current session?", "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return
        # otherwise ask the user what new file to open
        with wx.DirDialog(
                self, "Open Artifacts Directory",
                "AMT Directory",
                style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = dirDialog.GetPath()
            try:
                logging.info("Load directory: %s", pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot(os.path.basename(pathname), self.folder_image)
        self.decorate_tree(root, load(pathname))
        self.tree.Expand(root)


    def OnSave(self, e):
        LOGGER.info("Save")

    def OnSaveAs(self, e):
        LOGGER.info("Save As")

    def onLogEvent(self, event):
        msg = event.message.strip("\r") + "\n"
        self.logconsole.AppendText(msg)
        event.Skip()

    def OnClose(self, event):
        LOGGER.info("Close")

    def OnQuit(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()

        # delete the frame
        self.Destroy()


def main():
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
