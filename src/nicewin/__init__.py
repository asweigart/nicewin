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
"""

import ctypes
from ctypes import wintypes # We can't use ctypes.wintypes, we must import wintypes this way.

from constants import NULL, SW_FORCEMINIMIZE, SW_HIDE, SW_RESTORE, SW_SHOW, SW_SHOWMAXIMIZED, SW_SHOWMINIMIZED, FORMAT_MESSAGE_FROM_SYSTEM, FORMAT_MESSAGE_ALLOCATE_BUFFER, FORMAT_MESSAGE_IGNORE_INSERTS,  AW_ACTIVATE, AW_HIDE
from structs import POINT, RECT, WINDOWPLACEMENT


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

    TODO
    """
    def __init__(self, hWnd):
        """Create a Window object given an `hWnd` "window handle". TODO"""
        if not hWnd:
            raise NiceWinException('hWnd arg must be a nonzero integer')

        self.hWnd = hWnd


    def __eq__(self, other):
        return isinstance(other, Window) and other.hWnd == self.hWnd


    @property
    def window_text(self):
        """A read-only property for the title or caption in the top bar of
        the window."""
        return get_window_text(self)

    @window_text.setter
    def window_text(self, value):
        set_window_text(self, str(value))

    @property
    def is_visible(self):
        """Returns `True` if the window is visible, otherwise returns `False`.
        This property can be set to a bool, in which case the `hide()` or
        `show()` method is called. TODO - what counts as visible."""
        return is_window_visible(self)

    @is_visible.setter
    def is_visible(self, value):
        if value:
            self.show()
        else:
            self.hide()


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



def animate_window(windowObj, milliseconds, animationType):
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

    ctypes.windll.user32.AnimateWindow(windowObj.hWnd, milliseconds, animationType)



def bring_window_to_top(windowObj):
    """A nice wrapper for BringWindowToTop(). Brings the window to the top of
    the z-order, on top of all other windows.

    Syntax:
    BOOL BringWindowToTop(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-bringwindowtotop
    """
    result = ctypes.windll.user32.BringWindowToTop(windowObj.hWnd)
    if result == 0:
        _raiseWithLastError()


def close_window(windowObj):
    """A nice wrapper for CloseWindow(). Activates (puts in focus) the window
    and minimizes it, if it is not already minimized. This function is poorly
    named: it doesn't "destroy" the window.

    Syntax:
    BOOL CloseWindow(HWND hWnd);

    Additional Information:
    https://stackoverflow.com/questions/4904757/closewindow-vs-showwindowhwnd-sw-minimize

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-closewindow
    """
    result = ctypes.windll.user32.CloseWindow(windowObj.hWnd)
    if result == 0:
        _raiseWithLastError()


def destroy_window(windowObj):
    """A nice wrapper for DestroyWindow().

    Syntax:
    BOOL DestroyWindow(HWND hWnd);

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-destroywindow
    """
    result = ctypes.windll.user32.DestroyWindow(windowObj.hWnd)
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
        return hWnd


def get_client_rect(windowObj):
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
    result = ctypes.windll.user32.GetClientRect(windowObj.hWnd, ctypes.byref(rect))
    if result == 0:
        _raiseWithLastError()
    else:
        return (rect.left, rect.top, rect.right, rect.bottom)


def get_desktop_window():
    """A nice wrapper for GetDesktopWindow(). TODO

    Syntax:
    HWND GetDesktopWindow();

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getdesktopwindow
    """
    return ctypes.windll.user32.GetDesktopWindow()


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


def get_window(windowObj, relationship):
    """A nice wrapper for GetWindow(). TODO

    Syntax:
    HWND GetWindow(
      HWND hWnd,
      UINT uCmd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindow
    """
    hWnd = ctypes.windll.user32.GetWindow(windowObj.hWnd, relationship)
    if hWnd == NULL:
        _raiseWithLastError()
    else:
        return Window(hWnd)


def get_window_placement(windowObj):
    """A nice wrapper for GetWindowPlacement(). TODO

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
    result = ctypes.windll.user32.GetWindowPlacement(windowObj.hWnd, ctypes.byref(windowPlacement))
    if result == 0:
        _raiseWithLastError()
    else:
        return windowPlacement # TODO - finish this


def get_window_rect(windowObj):
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
    result = ctypes.windll.user32.GetWindowRect(windowObj.hWnd, ctypes.byref(rect))
    if result != 0:
        return (rect.left, rect.top, rect.right, rect.bottom)
    else:
        _raiseWithLastError()


def get_window_text(windowObj):
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
    textLenInCharacters = ctypes.windll.user32.GetWindowTextLengthW(windowObj.hWnd)
    stringBuffer = ctypes.create_unicode_buffer(textLenInCharacters + 1) # +1 for the \0 at the end of the null-terminated string.
    ctypes.windll.user32.GetWindowTextW(windowObj.hWnd, stringBuffer, textLenInCharacters + 1)

    # TODO it's ambiguous if an error happened or the title text is just empty. Look into this later.
    return stringBuffer.value


def is_window_visible(windowObj):
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
    return ctypes.windll.user32.IsWindowVisible(windowObj.hWnd) != 0


def peek_message():
    # TODO
    ctypes.windll.user32.PeekMessage()


def set_foreground_window(windowObj):
    """A nice wrapper for SetForegroundWindow(). TODO

    Syntax:
    BOOL SetForegroundWindow(
      HWND hWnd
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setforegroundwindow
    """
    result = ctypes.windll.user32.SetForegroundWindow(windowObj.hWnd)
    if result == 0: # There is no GetLastError() for this function.
        raise NiceWinException('Unable to set this window as the foreground window. For possible causes, see https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setforegroundwindow#remarks')


def set_window_text(windowObj, text):
    """A nice wrapper for SetWindowTextW(). TODO

    Syntax:
    BOOL SetWindowTextW(
      HWND    hWnd,
      LPCWSTR lpString
    );

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-setwindowtextw
    """
    result = ctypes.windll.user32.SetWindowTextW(windowObj.hWnd, text)
    if result == 0:
        _raiseWithLastError()


def show_window(windowObj, action):
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

    result = ctypes.windll.user32.ShowWindow(windowObj.hWnd, action)

    if result == 0:
        return 'window was previously hidden'
    else:
        return 'window was previously visible'


def show_window_async(windowObj, action):
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
    result = ctypes.windll.user32.ShowWindowAsync(windowObj.hWnd, action)
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


# TODO - need to test this
#def sound_sentry():
#    ctypes.windll.user32.SoundSentry()

w = get_foreground_window()
print(get_window_rect(w))