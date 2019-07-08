import traceback
import wx
import wx.aui
import wx.lib.newevent
import logging


def WXExceptionHook(etype, value, trace):
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


class WXLogHandler(logging.Handler):
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

