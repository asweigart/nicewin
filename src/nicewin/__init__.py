"""
NiceWin, a nicely-documented wrapper for several Windows API function calls.
By Al Sweigart al@inventwithpython.com

The primary aim of this module is more for educational purposes than practical
use. I'd recommend the venerable pywin32 module for Windows-related function
calling in your Python code. Please do examine the docstrings for these
functions.

This module is meant to make it easy to copy/paste example code into your own
programs as well.

If there are parts of this code that you don't understand, please contact
Al at al@inventwithpython.com with suggestions for what needs to be clarified.

NOTE: Al Sweigart is not a win32 or Windows system internals expert.

The best guides to learning to program Windows applications is Charles Petzold's
"Programming Windows" books, currently in its sixth edition, and the "Windows
Internals" books (Part 1 and Part2) by Yosifovich, Russinovich, Solomon, &
Ionescu.

Microsoft has great documentation on their Docs site (formerly known as MDN,
Microsoft Developer's Network) at
https://docs.microsoft.com/en-us/windows/desktop/api/index

But usually it's just easiest to google for the particular function you are
looking up.

Some things to note first about the Windows API:

* Function names in the Windows API are capitalized, like GetWindowText().
  Their Python equivalents will be written in snake_case.
* hWnd is a "window handle", which you can get from GetForegroundWindow()
  and other such functions. An hWnd as an integer that identifies a window.
* Many Windows API functions return an error code, and the actual output
  of the function is in a by-reference argument that was passed in.
* The returned error code only indicates an error happened. Call
  GetLastError() to get the integer error code and FormatMessage() to
  get the error message for that code.
* Many Windows API functions have am A and W suffix: The A is for versions
  that use Ansi (Ascii) text, while W is for "wide" (unicode) text. This
  module will use the W functions over the A functions.
* TODO - note about dealing with strings and allocating/freeing memory
  for them.


Note for developers and contributors:

The primary reason for this module is to ease Python programmers into the
win32 api. As such, if you'd like to contribute, please make note of the
following:

* The main functions should reflect the win32 function names, even if it
  doesn't quite make sense. For example, the LockSetForegroundWindow()
  function can both lock and unlock the ability to set the window to the
  foreground, but nevertheless we'll name the function
  lock_set_foreground_window() in NiceWin.
* However, the arguments and return values can be Pythonic and don't have to
  match the win32 API exactly.
* Documentation is important! Follow the docstring format used by
  functions in this module; include links to the Microsoft documentation
  or Stack Overflow links that explain concepts. Assume the users have
  no knowledge of Windows internals concepts.
* In general, we use the W functions, not the A functions. For example,
  message_box() calls MessageBoxW(), not MessageBoxA() or MessageBox().
"""

__version__ = '0.0.1'

import ctypes
from ctypes import wintypes # We can't use ctypes.wintypes, we must import wintypes this way.

from .constants import NULL, SW_FORCEMINIMIZE, SW_HIDE, SW_RESTORE, SW_SHOW, SW_SHOWMAXIMIZED, SW_SHOWMINIMIZED, FORMAT_MESSAGE_FROM_SYSTEM, FORMAT_MESSAGE_ALLOCATE_BUFFER, FORMAT_MESSAGE_IGNORE_INSERTS,  AW_ACTIVATE, AW_HIDE, LSFW_LOCK, LSFW_UNLOCK, MB_OKCANCEL, IDABORT, IDCANCEL, IDCONTINUE, IDIGNORE, IDNO, IDOK, IDRETRY, IDTRYAGAIN, IDYES, HWND_TOP, MONITOR_DEFAULTTONEAREST, MONITOR_DEFAULTTONULL, MONITOR_DEFAULTTOPRIMARY


from .structs import POINT, RECT, WINDOWPLACEMENT

import collections


# NOTE: `Rect` is a named tuple for use in Python, while structs.RECT represents
# the win32 RECT struct.
Rect = collections.namedtuple('Rect', 'left top right bottom')

class NiceWinException(Exception):
    """This class exists for any exceptions raised by the nicewin module. If
    nicewin raises any other exceptions, assume that that is a bug in this
    module."""
    pass


def _raiseWithLastError():
    """A helper function that raises NiceWinException using the error
    information from GetLastError() and FormatMessage()."""
    errorCode = ctypes.windll.kernel32.GetLastError()
    raise NiceWinException('Error code from Windows: %s - %s' % (errorCode, format_message(errorCode)))


class Window:
    """A class that represents a Window, to provide a richer representation
    than just a `hWnd` "window handle".

    Window handles are recycled, so the particular hWnd value could later be
    used for a different window.

    TODO
    """
    def __init__(self, hWnd):
        """Create a Window object given an `hWnd` "window handle". TODO"""
        if not hWnd:
            raise NiceWinException('hWnd arg must be a nonzero integer')

        self.hWnd = hWnd


    def __str__(self):
        r = get_window_text(self)
        width = r.right - r.left
        height = r.bottom - r.top
        return '<%s left="%s", top="%s", width="%s", height="%s", title="%s">' % (self.__class__.__name__, r.left, r.top, width, height, self.title)


    def __repr__(self):
        return '%s(hWnd=%s)' % (self.__class__.__name__, self.hWnd)


    def __eq__(self, other):
        return isinstance(other, Window) and other.hWnd == self.hWnd


    @property
    def title(self):
        """The string of the title or caption in the top bar of the window."""
        return get_window_text(self)

    @title.setter
    def title(self, value):
        set_window_text(self, str(value))


    @property
    def width(self):
        r = get_window_rect(self)
        return r.right - r.left

    @property
    def height(self):
        r = get_window_rect(self)
        return r.bottom - r.top

    @property
    def size(self):
        r = get_window_rect(self)
        return (r.right - r.left, r.bottom - r.top)

    @property
    def topleft(self):
        r = get_window_rect(self)
        return (r.left, r.top)

    @property
    def topright(self):
        r = get_window_rect(self)
        return (r.right, r.top)

    @property
    def bottomleft(self):
        r = get_window_rect(self)
        return (r.left, r.bottom)

    @property
    def bottomright(self):
        r = get_window_rect(self)
        return (r.right, r.bottom)

    @property
    def top(self):
        return get_window_rect(self).top

    @property
    def bottom(self):
        return get_window_rect(self).bottom

    @property
    def left(self):
        return get_window_rect(self).left

    @property
    def right(self):
        return get_window_rect(self).right


    @property
    def visible(self):
        """A bool for of the window is visible (shown) or not (hidden)."""
        return is_window_visible(self)

    @visible.setter
    def visible(self, value):
        if value:
            self.show()
        else:
            self.hide()


    @property
    def maximized(self):
        """A bool for if the window is maximized or not."""
        return is_zoomed(self)

    @maximized.setter
    def maximized(self, value):
        if value:
            self.maximize()
        else:
            if is_zoomed(self):
                # Already maximized, so restore the window.
                self.restore()
            else:
                # Not maximized, so do nothing.
                pass


    @property
    def minimized(self):
        """A bool for if the window is minimized or not."""
        return is_iconic(self)

    @minimized.setter
    def minimized(self, value):
        if value:
            self.minimize()
        else:
            if is_iconic(self):
                # Already minimized, so restore the window.
                open_icon(self)
            else:
                # Not minimized, so do nothing.
                pass


    # ShowWindow() methods:
    def hide(self):
        """Hide the window by making it invisible. Hiding is different from
        minimizing. It'll only reappear when `show()` is called on it.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        return show_window(self, SW_HIDE)


    def show(self):
        """Show the window by making it visible.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        return show_window(self, SW_SHOW)


    def force_minimize(self):
        """Minimizes this window to the taskbar, even if the thread is busy
        running other code.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        return show_window(self, SW_FORCEMINIMIZE)


    def maximize(self):
        """Maximizes this window to fill the screen.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        show_window(self, SW_SHOWMAXIMIZED)


    def minimize(self):
        """Minimize this window to the taskbar.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        show_window(self, SW_SHOWMINIMIZED)


    def restore(self):
        """Restores this window from the minimized or maximized state.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        show_window(self, SW_RESTORE)


    def bring_to_top(self):
        """Moves this window to the top of the z-order in front of other
        windows.

        Returns either 'window was previously hidden' or
        'window was previously visible'.
        """
        bring_window_to_top(self)



def animate_window(window_obj, milliseconds, animationType):
    """A nice wrapper for AnimateWindow(). Allows you to animate a window while
    showing or hiding it. There are four types of animation: roll, slide,
    collapse or expand, and alpha-blended fade.

    Syntax:
    BOOL AnimateWindow(
      HWND  hWnd,
      DWORD dwTime,
      DWORD dwFlags
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-animatewindow
    """
    if (animationType & AW_ACTIVATE != 0) and (animationType & AW_HIDE != 0):
        raise NiceWinException('animationType can\'t be both AW_ACTIVATE and AW_HIDE')

    ctypes.windll.user32.AnimateWindow(window_obj.hWnd, milliseconds, animationType)



def bring_window_to_top(window_obj):
    """A nice wrapper for BringWindowToTop(). Brings the window to the top of
    the z-order, on top of all other windows.

    Additional info:
    https://stackoverflow.com/questions/1544179/what-are-the-differences-between-bringwindowtotop-setforegroundwindow-setwindo

    TODO NOTE: This doesn't actually seem to work. You might want to try
    set_foreground_window() instead. I'm not sure what the difference is.

    Syntax:
    BOOL BringWindowToTop(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-bringwindowtotop
    """
    result = ctypes.windll.user32.BringWindowToTop(window_obj.hWnd)
    if result == 0:
        _raiseWithLastError()


def clip_cursor(left=None, top=None, right=None, bottom=None):
    """A nice wrapper for ClipCursor(). Restricts the mouse cursor to the are
    on the screen dictated by `left`, `top`, `right`, and `bottom`.

    If no arguments are passed, the cursor is free to move anywhere.

    Syntax:
    BOOL ClipCursor(
      const RECT *lpRect
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-clipcursor

    An example of confining a cursor:
    https://docs.microsoft.com/en-us/windows/desktop/menurc/using-cursors#confining-a-cursor
    """
    if (left is None) or (top is None) or (right is None) or (bottom is None):
        if (left is None) and (top is None) and (right is None) and (bottom is None):
            # Call ClipCursor() and pass NULL.
            result = ctypes.windll.user32.ClipCursor(NULL)
        else:
            # One of the parameters is None, but not all of them.
            raise NiceWinException('either all args must be None or none of the args can be None')
    else:
        # All of the args have been specified.
        rect = RECT()
        rect.left = left
        rect.top = top
        rect.right = right
        rect.bottom = bottom
        result = ctypes.windll.user32.ClipCursor(rect) # TODO i dont' think I'm passing this correctly.

    if result != 0:
        return True
    else:
        _raiseWithLastError()



def close_window(window_obj):
    """A nice wrapper for CloseWindow(). Activates (puts in focus) the window
    and minimizes it, if it is not already minimized. This function is poorly
    named: it doesn't "destroy" the window.

    According to https://stackoverflow.com/a/4904953/1893164, CloseWindow()
    is just an older function like IsIconic() and IsZoomed(). It is extended
    by ShowWindow().



    Syntax:
    BOOL CloseWindow(HWND hWnd);

    Additional Information:
    https://stackoverflow.com/questions/4904757/closewindow-vs-showwindowhwnd-sw-minimize

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-closewindow
    """
    result = ctypes.windll.user32.CloseWindow(window_obj.hWnd)
    if result == 0:
        _raiseWithLastError()


def destroy_window(window_obj):
    """A nice wrapper for DestroyWindow().

    This can only close a window created by the same thread running this code.
    If you want to close a different window, call PostMessageA() and pass the
    WM_CLOSE message.

    Syntax:
    BOOL DestroyWindow(HWND hWnd);

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-destroywindow
    """
    result = ctypes.windll.user32.DestroyWindow(window_obj.hWnd)
    if result == NULL:
        _raiseWithLastError()


def find_window(windowName):
    """A nice wrapper for FindWindowW(). TODO

    Syntax:
    HWND FindWindowW(
      LPCWSTR lpClassName,
      LPCWSTR lpWindowName
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-findwindoww

    Additional information about Window Classes:
    https://docs.microsoft.com/en-us/windows/desktop/winmsg/window-classes
    """
    hWnd = ctypes.windll.user32.FindWindowW(NULL, windowName)
    if hWnd == NULL:
        _raiseWithLastError()
    else:
        return Window(hWnd)


def format_message(errorCode):
    """A nice wrapper for FormatMessageW(). TODO

    Syntax:
    DWORD FormatMessage(
      DWORD   dwFlags,
      LPCVOID lpSource,
      DWORD   dwMessageId,
      DWORD   dwLanguageId,
      LPTSTR  lpBuffer,
      DWORD   nSize,
      va_list *Arguments
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-formatmessagew

    Additional information:
    https://stackoverflow.com/questions/18905702/python-ctypes-and-mutable-buffers
    https://stackoverflow.com/questions/455434/how-should-i-use-formatmessage-properly-in-c
    """
    lpBuffer = wintypes.LPWSTR()

    ctypes.windll.kernel32.FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_IGNORE_INSERTS,
                                          NULL,
                                          errorCode,
                                          0, # dwLanguageId
                                          ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR),
                                          0, # nSize
                                          NULL)
    msg = lpBuffer.value.rstrip()
    ctypes.windll.kernel32.LocalFree(lpBuffer) # Free the memory allocated for the error message's buffer.
    return msg


def get_active_window():
    """A nice wrapper for GetActiveWindow().

    Syntax:
    HWND GetActiveWindow();

    According to https://stackoverflow.com/questions/3940346/foreground-vs-active-window
    the "active window" is the window attached to the thread calling this
    function, while the "foreground window" is the window that is currently
    getting input.

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getactivewindow
    """
    hWnd = ctypes.windll.user32.GetActiveWindow()
    if hWnd == 0:
        return None # Note that this function doesn't use GetLastError().
    else:
        return Window(hWnd)


def get_client_rect(window_obj):
    """A nice wrapper for GetClientRect(). TODO

    Syntax:
    BOOL GetClientRect(
      HWND   hWnd,
      LPRECT lpRect
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getclientrect

    Additional documentation about RECT structures:
    https://msdn.microsoft.com/en-us/library/windows/desktop/dd162897(v=vs.85).aspx
    """
    rect = RECT()
    result = ctypes.windll.user32.GetClientRect(window_obj.hWnd, ctypes.byref(rect))
    if result == 0:
        _raiseWithLastError()
    else:
        return (rect.left, rect.top, rect.right, rect.bottom)


def get_cursor_pos():
    """A nice wrapper for GetCursorPos(). This returns an (x, y) tuple of the
    mouse cursor's position, in screen coordinates.

    Syntax:
    BOOL GetCursorPos(
      LPPOINT lpPoint
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getcursorpos
    """

    cursor = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return (cursor.x, cursor.y)


def get_cursor():
    """A nice wrapper for GetCursor(). TODO

    Syntax:
    HCURSOR GetCursor();

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getcursor
    """
    pass # TODO


def get_cursor_info():
    """A nice wrapper for GetCursorInfo(). TODO

    Syntax:
    BOOL GetCursorInfo(
      PCURSORINFO pci
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getcursorinfo
    """
    pass # TODO


def get_desktop_window():
    """A nice wrapper for GetDesktopWindow(). TODO

    Syntax:
    HWND GetDesktopWindow();

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getdesktopwindow
    """
    return Window(ctypes.windll.user32.GetDesktopWindow())


def get_drives():
    """A nice wrapper for _getdrives(). TODO

    Syntax:
    unsigned long _getdrives( void );

    Microsoft Documentation:
    https://msdn.microsoft.com/en-us/library/xdhk0xd2.aspx
    """
    available_drives = []
    available_drive_flags = ctypes.cdll.msvcrt._getdrives()
    for flag in range(26):
        if available_drive_flags & (1 << flag):
            available_drives.append('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[flag])
    return available_drives


def get_foreground_window():
    """A nice wrapper for GetForegroundWindow().

    Syntax:
    HWND GetForegroundWindow();

    According to https://stackoverflow.com/questions/3940346/foreground-vs-active-window
    the "active window" is the window attached to the thread calling this
    function, while the "foreground window" is the window that is currently
    getting input.

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getforegroundwindow
    """
    # https://stackoverflow.com/questions/3940346/foreground-vs-active-window
    hWnd = ctypes.windll.user32.GetForegroundWindow()
    if hWnd == 0:
        return None # Note that this function doesn't use GetLastError().
    else:
        return Window(hWnd)


def get_last_error():
    """A nice wrapper for GetLastError(). When Windows API function call fail,
    they usually only indicate that an error happened, not what the actual
    error was. It is convention to call GetLastError() to get the actual error
    code, and then FormatMessage() to get the error message based on this code.

    Syntax:
    DWORD GetLastError();

    Microsoft Documentation:
    https://msdn.microsoft.com/en-us/d852e148-985c-416f-a5a7-27b6914b45d4
    """
    return ctypes.windll.kernel32.GetLastError()


def get_user_name():
    """TODO

    TODO - This currently doesn't work and returns a blank string.
    """
    # Copied from https://sjohannes.wordpress.com/2010/06/19/win32-python-getting-users-display-name-using-ctypes/
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, nameBuffer, size)
    return nameBuffer.value


def get_window(window_obj, relationship):
    """A nice wrapper for GetWindow(). TODO

    Syntax:
    HWND GetWindow(
      HWND hWnd,
      UINT uCmd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindow
    """
    hWnd = ctypes.windll.user32.GetWindow(window_obj.hWnd, relationship)
    if hWnd == NULL:
        _raiseWithLastError()
    else:
        return Window(hWnd)


def get_window_placement(window_obj):
    """A nice wrapper for GetWindowPlacement(). TODO

    "Retrieves the show state and the restored, minimized, and maximized positions of the specified window."

    Syntax:
    BOOL GetWindowPlacement(
      HWND            hWnd,
      WINDOWPLACEMENT *lpwndpl
    );

    Microsoft Documention:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindowplacement

    Additional documentation for WINDOWPLACEMENT:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-tagwindowplacement
    """
    windowPlacement = WINDOWPLACEMENT
    result = ctypes.windll.user32.GetWindowPlacement(window_obj.hWnd, ctypes.byref(windowPlacement))
    if result == 0:
        _raiseWithLastError()
    else:
        return windowPlacement # TODO - finish this


def get_window_rect(window_obj):
    """A nice wrapper for GetWindowRect(). TODO

    Syntax:
    BOOL GetWindowRect(
      HWND   hWnd,
      LPRECT lpRect
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindowrect
    """
    rect = RECT()
    result = ctypes.windll.user32.GetWindowRect(window_obj.hWnd, ctypes.byref(rect))
    if result != 0:
        return Rect(rect.left, rect.top, rect.right, rect.bottom)
    else:
        _raiseWithLastError()


def get_window_text(window_obj):
    """A nice wrapper for GetWindowTextW(). TODO

    Syntax:
    int GetWindowTextW(
      HWND   hWnd,
      LPWSTR lpString,
      int    nMaxCount
    );

    int GetWindowTextLengthW(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindowtextw
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindowtextlengthw
    """
    textLenInCharacters = ctypes.windll.user32.GetWindowTextLengthW(window_obj.hWnd)
    stringBuffer = ctypes.create_unicode_buffer(textLenInCharacters + 1) # +1 for the \0 at the end of the null-terminated string.
    ctypes.windll.user32.GetWindowTextW(window_obj.hWnd, stringBuffer, textLenInCharacters + 1)

    # TODO it's ambiguous if an error happened or the title text is just empty. Look into this later.
    return stringBuffer.value


def get_window_thread_process_id(window_obj):
    """A nice wrapper for GetWindowThreadProcessId(). Returns a tuple of the
    thread id (tid) of the thread that created the specified window, and the
    process id that created the window.

    Syntax:
    DWORD GetWindowThreadProcessId(
      HWND    hWnd,
      LPDWORD lpdwProcessId
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindowthreadprocessid
    """
    pid = wintypes.DWORD()
    tid = ctypes.windll.user32.GetWindowThreadProcessId(window_obj.hWnd, ctypes.byref(pid))
    return tid, pid.value


def is_child(parent_window_obj, child_window_obj):
    """A nice wrapper for IsChild(). Returns `True` if `child_window_obj` is a
    child window of `parent_window_obj`.

    Syntax:
    BOOL IsChild(
      HWND hWndParent,
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-ischild
    """
    return ctypes.windll.user32.IsChild(parent_window_obj.hWnd, child_window_obj.hWnd) != 0


def is_gui_thread(convert_to_gui=False):
    """A nice wrapper for IsGuiThread(). If `convert_to_gui` is `True`, then
    the thread will be converted to one.

    TODO - write more about gui threads

    Syntax:
    BOOL IsGUIThread(
      BOOL bConvert
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-isguithread

    TODO - handle ERROR_NOT_ENOUGH_MEMORY case
    """
    return ctypes.windll.user32.IsGuiThread(convert_to_gui) != 0


def is_iconic(window_obj):
    """A nice wrapper for IsIconic(). Returns `True` if `window_obj` is
    "iconic", that is, minimized.

    According to https://stackoverflow.com/a/4904953/1893164, IsIconic()
    is just an older function like CloseWindow() and IsZoomed(). It is extended
    by ShowWindow().

    Syntax:
    BOOL IsIconic(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-isiconic
    """
    return ctypes.windll.user32.IsIconic(window_obj.hWnd) != 0


def is_process_dpi_aware():
    """A nice wrapper for IsProcessDPIAware(). TODO

    Syntax:
    BOOL IsProcessDPIAware();

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-isprocessdpiaware
    """
    return bool(ctypes.windll.user32.IsProcessDPIAware());


def is_window(window_obj):
    """A nice wrapper for IsWindow(). Returns `True` if `window_obj` identifies
    an existing window.

    A thread shouldn't call is_window() on a window that it didn't create
    because it could later be destroyed, making the return value out of date.

    Window handles are recycled, so the particular hWnd value could later be
    used for a different window.

    Syntax:
    BOOL IsWindow(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-iswindow
    """
    return ctypes.windll.user32.IsWindow(window_obj.hWnd) != 0


def is_window_unicode(window_obj):
    """A nice wrapper for IsWindowUnicode(). Returns `True` if the specified
    window is a native Unicode window. The character set of a window is
    determined by the window class that was registered (through
    RegisterClass()).

    Syntax:
    BOOL IsWindowUnicode(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-iswindowunicode
    """
    return ctypes.windll.user32.IsWindowUnicode(window_obj.hWnd) != 0


def is_window_visible(window_obj):
    """A nice wrapper for IsWindowVisible(). TODO

    Syntax:
    BOOL IsWindowVisible(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-iswindowvisible

    WS_VISIBLE discussed in:
    https://docs.microsoft.com/en-us/windows/desktop/winmsg/window-styles
    """
    return ctypes.windll.user32.IsWindowVisible(window_obj.hWnd) != 0


def is_zoomed(window_obj):
    """A nice wrapper for IsZoomed(). Returns `True` if the specified window
    is "zoomed", that is, maximized.

    According to https://stackoverflow.com/a/4904953/1893164, IsZoomed()
    is just an older function like IsIconic() and CloseWindow(). It is extended
    by ShowWindow().

    Syntax:
    BOOL IsZoomed(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-iszoomed
    """
    return ctypes.windll.user32.IsZoomed(window_obj.hWnd) != 0


def lock_set_foreground_window(lock=True):
    """A nice wrapper for LockSetForegroundWindow(). By passing `LSFW_LOCK` for
    `lock`, you can disable calls to the SetForegroundWindow() function.

    Syntax:
    BOOL LockSetForegroundWindow(
      UINT uLockCode
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-locksetforegroundwindow
    """
    result = ctypes.windll.user32.LocSetForegroundWindow(LSFW_LOCK if lock else LSFW_UNLOCK)
    if result == 0:
        _raiseWithLastError()
    else:
        return True


def logical_to_physical_point(window_obj, logical_x, logical_y):
    """A nice wrapper for LogicalToPhysicalPoint(). A tuple of (x, y) physical
    point coordinates is returned matching the logical point in `window_obj`.

    TODO - I don't think this function works. It keeps returning 0, 0.

    Syntax:
    BOOL LogicalToPhysicalPoint(
      HWND    hWnd,
      LPPOINT lpPoint
    );

    "Currently MessageBoxEx and MessageBox work the same way."

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-logicaltophysicalpoint
    """
    physicalPoint = POINT()
    ctypes.windll.user32.LogicalToPhysicalPoint(window_obj.hWnd,
                                                ctypes.byref(physicalPoint))
    return (physicalPoint.x, physicalPoint.y)


def message_box(owner_window_obj, text, caption, box_type=MB_OKCANCEL):
    """A nice wrapper for MessageBoxW(). Displays a modal dialog box with a
    system icon, set of buttons, and message. Returns an integer that
    indicates which button the user clicked.

    Syntax:
    int MessageBoxW(
      HWND    hWnd,
      LPCWSTR lpText,
      LPCWSTR lpCaption,
      UINT    uType
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-messageboxw
    """
    result = ctypes.windll.user32.MessageBoxW(owner_window_obj.hWnd,
                                             text,
                                             caption,
                                             box_type)
    if result == 0:
        _raiseWithLastError()
    else:
        return {IDABORT: 'abort',
                IDCANCEL: 'cancel',
                IDCONTINUE: 'continue',
                IDIGNORE: 'ignore',
                IDNO: 'no',
                IDOK: 'ok',
                IDRETRY: 'retry',
                IDTRYAGAIN: 'try again',
                IDYES: 'yes'}[result]


def move_window(window_obj, x, y, width, height, repaint=True):
    """A nice wrapper for MoveWindow(). The dimensions of the window specified
    by `window_obj` are moved and resized so that the topleft corner is at
    `x` and `y`, with a size given by `width` and `height`.

    Syntax:
    BOOL MoveWindow(
      HWND hWnd,
      int  X,
      int  Y,
      int  nWidth,
      int  nHeight,
      BOOL bRepaint
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-movewindow
    """
    result = ctypes.windll.user32.MoveWindow(window_obj.hWnd, x, y, width, height, repaint)
    if result == 0:
        _raiseWithLastError()
    else:
        return True


def open_icon(window_obj):
    """A nice wrapper for OpenIcon(). This function restores a minimized, that
    is, iconic, window to its previous size and position. Then it activates,
    that is, focuses, the window.

    Syntax:
    BOOL OpenIcon(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-openicon
    """
    result = ctypes.windll.user32.OpenIcon(window_obj.hWnd)
    if result == 0:
        _raiseWithLastError()
    else:
        return True


def physical_to_logical_point(window_obj, physical_x, physical_y):
    """A nice wrapper for PhysicalToLogicalPoint(). Returns the logical point
    of `physical_x` and `physical_y` in the `window_obj`.

    TODO - this doesn't work for now, it always returns (0, 0)

    Syntax:
    BOOL PhysicalToLogicalPoint(
      HWND    hWnd,
      LPPOINT lpPoint
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-physicaltologicalpoint
    """
    logicalPoint = POINT()
    ctypes.windll.user32.PhysicalToLogicalPoint(window_obj.hWnd,
                                                ctypes.byref(logicalPoint))
    return (logicalPoint.x, logicalPoint.y)



def peek_message():
    # TODO
    ctypes.windll.user32.PeekMessage()


def set_foreground_window(window_obj):
    """A nice wrapper for SetForegroundWindow(). TODO

    Syntax:
    BOOL SetForegroundWindow(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setforegroundwindow
    """
    result = ctypes.windll.user32.SetForegroundWindow(window_obj.hWnd)
    if result == 0: # There is no GetLastError() for this function.
        raise NiceWinException('Unable to set this window as the foreground window. For possible causes, see https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setforegroundwindow#remarks')


def set_window_pos(window_obj, left, top, width, height, z=HWND_TOP, flags=0):
    """A nice wrapper for SetWindowPos(). While SetWindowPos() is similar to
    MoveWindow(), you can consider it to be a sort of "MoveWindowEx()".

    "Changes the size, position, and Z order of a child, pop-up, or top-level window. These windows are ordered according to their appearance on the screen. The topmost window receives the highest rank and is the first window in the Z order."
    Syntax:
    BOOL SetWindowPos(
      HWND hWnd,
      HWND hWndInsertAfter,
      int  X,
      int  Y,
      int  cx,
      int  cy,
      UINT uFlags
    );

    Microsot Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setwindowpos

    https://blogs.msdn.microsoft.com/oldnewthing/20090323-00/?p=18733/
    """
    result = ctypes.windll.user32.SetWindowPos(window_obj.hWnd, z, left, top, width, height, flags)
    if result == 0:
        _raiseWithLastError()


def set_window_text(window_obj, text):
    """A nice wrapper for SetWindowTextW(). TODO

    Syntax:
    BOOL SetWindowTextW(
      HWND    hWnd,
      LPCWSTR lpString
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setwindowtextw
    """
    result = ctypes.windll.user32.SetWindowTextW(window_obj.hWnd, text)
    if result == 0:
        _raiseWithLastError()


def show_window(window_obj, action):
    """"A nice wrapper for ShowWindow(). TODO

    The `action` arg is one of the following:
    SW_FORCEMINIMIZE, SW_HIDE, SW_MAXIMIZE, SW_MINIMIZE, SW_RESTORE, SW_SHOW,
    SW_SHOWDEFAULT, SW_SHOWMAXIMIZED, SW_SHOWMINIMIZED, SW_SHOWMINNOACTIVE,
    SW_SHOWNA, SW_SHOWNOACTIVATE, SW_SHOWNORMAL
    See https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindow#parameters

    Syntax:
    BOOL ShowWindow(
      HWND hWnd,
      int  nCmdShow
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindow
    """

    result = ctypes.windll.user32.ShowWindow(window_obj.hWnd, action)

    if result == 0:
        return 'window was previously hidden'
    else:
        return 'window was previously visible'


def show_window_async(window_obj, action):
    """A nice wrapper for ShowWindowAsync(). TODO - doesn't wait for action to complete before returning.

    The `action` arg is one of the following:
    SW_FORCEMINIMIZE, SW_HIDE, SW_MAXIMIZE, SW_MINIMIZE, SW_RESTORE, SW_SHOW,
    SW_SHOWDEFAULT, SW_SHOWMAXIMIZED, SW_SHOWMINIMIZED, SW_SHOWMINNOACTIVE,
    SW_SHOWNA, SW_SHOWNOACTIVATE, SW_SHOWNORMAL
    See https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindow#parameters

    Syntax:
    BOOL ShowWindowAsync(
      HWND hWnd,
      int  nCmdShow
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindowasync
    """
    result = ctypes.windll.user32.ShowWindowAsync(window_obj.hWnd, action)
    return result != 0 # Note that this function doesn't use GetLastError().


def wait_message():
    """A nice wrapper for WaitMessage(). TODO

    Syntax:
    BOOL WaitMessage();

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-waitmessage
    """
    result = ctypes.windll.user32.WaitMessage()
    return result != 0 # Note that this function doesn't use GetLastError().


def window_from_physical_point(x, y):
    """A nice wrapper for WindowFromPhysicalPoint. TODO

    Syntax:
    HWND WindowFromPhysicalPoint(
      POINT Point
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-windowfromphysicalpoint

    Additional Information:
    https://stackoverflow.com/questions/4324954/whats-the-difference-between-windowfromphysicalpoint-and-windowfrompoint

    Documentation on the POINT structure:
    http://msdn.microsoft.com/en-us/library/windows/desktop/dd162805(v=vs.85).aspx
    """
    cursor = POINT()
    cursor.x = x
    cursor.y = y
    hWnd = ctypes.windll.user32.WindowFromPhysicalPoint(ctypes.byref(cursor))
    if hWnd == 0:
        return None
    else:
        return Window(hWnd)


def window_from_point(x, y):
    """A nice wrapper for WindowFromPoint. TODO

    Syntax:
    HWND WindowFromPoint(
      POINT Point
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-windowfrompoint

    Additional Information:
    https://stackoverflow.com/questions/4324954/whats-the-difference-between-windowfromphysicalpoint-and-windowfrompoint

    Documentation on the POINT structure:
    http://msdn.microsoft.com/en-us/library/windows/desktop/dd162805(v=vs.85).aspx
    """
    cursor = POINT()
    hWnd = ctypes.windll.user32.WindowFromPhysicalPoint(ctypes.byref(cursor))
    if hWnd == 0:
        return None
    else:
        return Window(hWnd)


def get_scale_factor_for_device():
    """A nice wrapper for GetScaleFactorForDevice. TODO

    Syntax:
    DEVICE_SCALE_FACTOR GetScaleFactorForDevice(
      DISPLAY_DEVICE_TYPE deviceType
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/shellscalingapi/nf-shellscalingapi-getscalefactorfordevice

    Documentation on the DEVICE_SCALE_FACTOR enum:
    https://docs.microsoft.com/en-us/windows/desktop/api/shtypes/ne-shtypes-device_scale_factor

    Documentation on the DISPLAY_DEVICE_TYPE enum:
    https://docs.microsoft.com/en-us/windows/desktop/api/shellscalingapi/ne-shellscalingapi-display_device_type
    """

    # TODO - returns int 150 for 150% scaled monitor. Arg 0 is "primary device" and 1 is "immersive device".
    return ctypes.windll.shcore.GetScaleFactorForDevice(0)


def monitor_from_point(x, y, dwFlags=MONITOR_DEFAULTTONEAREST):
    """A nice wrapper for MonitorFromPoint. TODO

    Returns a handle for a monitor. TODO

    Syntax:
    HMONITOR MonitorFromPoint(
      POINT pt,
      DWORD dwFlags
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-monitorfrompoint

    Documentation on POINT structure:
    https://docs.microsoft.com/previous-versions//dd162805(v=vs.85)

    The dwFlags parameter is one of the following:
      MONITOR_DEFAULTTONEAREST, MONITOR_DEFAULTTONULL, MONITOR_DEFAULTTOPRIMARY
    """
    p = POINT()
    p.x = x
    p.y = y
    return ctypes.windll.user32.MonitorFromPoint(p, dwFlags)


def monitor_from_rect(left, top, right, bottom, dwFlags=MONITOR_DEFAULTTONEAREST):
    """A nice wrapper for MonitorFromRect. TODO

    Syntax:
    HMONITOR MonitorFromRect(
      LPCRECT lprc,
      DWORD   dwFlags
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-monitorfromrect

    Documentation on RECT structure:
    https://docs.microsoft.com/en-us/windows/desktop/api/windef/ns-windef-rect

    The dwFlags parameter is one of the following:
      MONITOR_DEFAULTTONEAREST, MONITOR_DEFAULTTONULL, MONITOR_DEFAULTTOPRIMARY
    """
    rect = RECT()
    rect.left = left
    rect.top = top
    rect.right = right
    rect.bottom = bottom
    return ctypes.windll.user32.MonitorFromRect(ctypes.byref(rect), dwFlags)

def monitor_from_window(hWnd, dwFlags=MONITOR_DEFAULTTONEAREST):
    """A nice wrapper for MonitorFromWindow. TODO

    Syntax:
    HMONITOR MonitorFromWindow(
      HWND  hwnd,
      DWORD dwFlags
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/Winuser/nf-winuser-monitorfromwindow

    The dwFlags parameter is one of the following:
      MONITOR_DEFAULTTONEAREST, MONITOR_DEFAULTTONULL, MONITOR_DEFAULTTOPRIMARY
    """
    if isinstance(hWnd, Window):
        # If hWnd is actually a Window object, use it's hWnd attribute.
        hWnd = hWnd.hWnd

    return ctypes.windll.user32.MonitorFromWindow(hWnd, dwFlags)


def get_monitor_from_window(hMonitor):
    """A nice wrapper for GetMonitorFromWindowA. TODO

    Syntax:
    BOOL GetMonitorInfoA(
      HMONITOR      hMonitor,
      LPMONITORINFO lpmi
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/Winuser/nf-winuser-getmonitorinfoa

    Documentation on the TODO
    """


# TODO - need to test this
#def sound_sentry():
#    ctypes.windll.user32.SoundSentry()


def get_dpi_for_monitor(hMonitor):
    """A nice wrappr for GetDpiForMonitor. TODP

    Syntax:
    HRESULT GetDpiForMonitor(
      HMONITOR         hmonitor,
      MONITOR_DPI_TYPE dpiType,
      UINT             *dpiX,
      UINT             *dpiY
    );

    Microsoft Documnetation:
    https://docs.microsoft.com/en-us/windows/desktop/api/shellscalingapi/nf-shellscalingapi-getdpiformonitor

    """
    #ctypes.windll.shcore.GetDpiForMonitor()