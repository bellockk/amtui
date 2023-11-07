import os
import sys
import wx
import wx.aui
import wx.adv
import wx.lib.newevent
import wx.lib.gridmovers
import wx.propgrid
from wx.lib.wordwrap import wordwrap
import logging

__all__ = ['main']

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])

from amt.load import load
sys.path.insert(0, dirName)
import images
from custom_status_bar import CustomStatusBar
from log_handler import WXLogHandler
from log_handler import WXExceptionHook
from artifact_tree import ArtifactTree


class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='AMT',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # Install Error Hook
        sys.excepthook = WXExceptionHook

        # Create a logger for this class
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        handler = WXLogHandler(self)
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
            images.square_brackets.Image.Scale(16, 16).ConvertToBitmap())
        self.file_dictionary_image = self.image_list.Add(
            images.curly_brackets.Image.Scale(16, 16).ConvertToBitmap())
        self.list_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_LIST_VIEW, wx.ART_OTHER, wx.Size(16, 16)))
        self.dictionary_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_REPORT_VIEW, wx.ART_OTHER, wx.Size(16, 16)))
        self.record_image = self.image_list.Add(wx.ArtProvider.GetBitmap(
            wx.ART_EXECUTABLE_FILE, wx.ART_OTHER, wx.Size(16, 16)))
        self.tree = ArtifactTree(self, -1, wx.Point(0, 0), wx.Size(160, 250),
                                 wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        self.tree.AssignImageList(self.image_list)
        text2 = wx.TextCtrl(self, -1, '',
                            wx.DefaultPosition, wx.Size(200, 150),
                            wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY |
                            wx.HSCROLL)
        text2.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False,
                              u'Consolas'))

        # text3 = wx.TextCtrl(self, -1, 'Main content window',
        #                     wx.DefaultPosition, wx.Size(200, 150),
        #                     wx.NO_BORDER | wx.TE_MULTILINE)
        self.logconsole = text2

        self.pg = wx.propgrid.PropertyGrid(self, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER |
                wx.propgrid.PG_AUTO_SORT | wx.propgrid.PG_TOOLBAR)
        self.pg.Append(wx.propgrid.StringProperty('String', value='hi'))
        self.pg.Append(wx.propgrid.StringProperty('String2', value='there'))

        # add the panes to the manager
        self._mgr.AddPane(self.tree, wx.LEFT, 'Artifact Tree')
        self._mgr.AddPane(text2, wx.aui.AuiPaneInfo().Name(
            'Log Console').Caption('Log Console').Bottom().CloseButton(True))
        self._mgr.AddPane(self.pg, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)

        # Create Status Bar
        self.status_bar = CustomStatusBar(self)
        self.SetStatusBar(self.status_bar)
        self.status_bar.SetStatusText("Welcome to AMT")

        self.content_not_saved = False

        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(WXLogHandler.EVT_WX_LOG_EVENT, self.onLogEvent)

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

        self.Bind(wx.EVT_MENU, self.on_new, new_button)
        self.Bind(wx.EVT_MENU, self.on_open_file, open_file_button)
        self.Bind(wx.EVT_MENU, self.on_open_directory, open_directory_button)
        self.Bind(wx.EVT_MENU, self.on_save, self.save_button)
        self.Bind(wx.EVT_MENU, self.on_save_as, self.save_as_button)
        self.Bind(wx.EVT_MENU, self.on_close, self.close_button)
        self.Bind(wx.EVT_MENU, self.on_quit, quit_button)

        menubar.Append(fileMenu, '&File')

        # View Menu
        view_menu = wx.Menu()
        self.view_log = view_menu.AppendCheckItem(wx.ID_ANY, 'Show Log Window')
        self.view_log.Check(True)
        menubar.Append(view_menu, '&View')
 
        self.Bind(wx.EVT_MENU, self.on_view_log, self.view_log)

        # Help Menu
        help_menu = wx.Menu()
        about = help_menu.Append(wx.ID_ANY, 'About')
        menubar.Append(help_menu, '&Help')

        self.Bind(wx.EVT_MENU, self.on_about, about)

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

    def on_new(self, e):
        logging.info("New")

    def on_open_file(self, e):
        logging.info("Open File")
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

    def on_open_directory(self, e):
        logging.info("Open Directory")
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

    def on_save(self, event):
        logging.info("Save")

    def on_save_as(self, event):
        logging.info("Save As")

    def onLogEvent(self, event):
        msg = event.message.strip("\r") + "\n"
        self.logconsole.AppendText(msg)
        event.Skip()

    def on_close(self, event):
        logging.info("Close")

    def on_quit(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()

        # delete the frame
        self.Destroy()

    def on_view_log(self, event):
        self.log.info('Toggle view Log')
        self.log_console_visibility(event.IsChecked())

    def on_pane_close(self, event):
        caption = event.GetPane().caption
        self.log.info(f'Closed Pane {caption}')
        if caption == 'Log Console':
            self.log_console_visibility(False)
            event.Veto()

    def log_console_visibility(self, visible: bool):
        self.view_log.Check(visible)
        self._mgr.GetPane('Log Console').Show(visible)
        self._mgr.Update()

    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.Name = "AMT GUI"
        info.Version = "1.2.3"
        info.Copyright = "(c) 2013-2020 Kenneth E. Bellock"
        info.Description = wordwrap(
            'A user interface for working with the artifact management tool.',
            350, wx.ClientDC(self))
        info.WebSite = ("https://github.com/amt", "AMT Homepage")
        info.Developers = ["Kenneth E. Bellock"]
        info.License = wordwrap('', 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.adv.AboutBox(info)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
