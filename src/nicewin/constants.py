
NULL = 0

# These SW_ constants are used for ShowWindow() and are documented at
# https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindow#parameters
SW_FORCEMINIMIZE = 11
SW_HIDE = 0
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWDEFAULT = 10
SW_SHOWMAXIMIZED = 3
SW_SHOWMINIMIZED = 2
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_SHOWNOACTIVATE = 4
SW_SHOWNORMAL = 1

# These FORMAT_MESSAGE_ constants are used for FormatMesage() and are
# documented at https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-formatmessage#parameters
FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x00000100
FORMAT_MESSAGE_ARGUMENT_ARRAY = 0x00002000
FORMAT_MESSAGE_FROM_HMODULE = 0x00000800
FORMAT_MESSAGE_FROM_STRING = 0x00000400
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200
FORMAT_MESSAGE_MAX_WIDTH_MASK = 0x000000FF

# Language IDs documented at https://docs.microsoft.com/en-us/windows/desktop/Intl/language-identifier-constants-and-strings
# More documentation at https://docs.microsoft.com/en-us/windows/desktop/Intl/language-identifiers
LANG_NEUTRAL = 0x00
SUBLANG_DEFAULT = 0x01

# These AW_ constants are used for AnimateWindow() and are documented at
# https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-animatewindow
AW_ACTIVATE = 0x00020000
AW_BLEND = 0x00080000
AW_CENTER = 0x00000010
AW_HIDE = 0x00010000
AW_HOR_POSITIVE = 0x00000001
AW_HOR_NEGATIVE = 0x00000002
AW_SLIDE = 0x00040000
AW_VER_POSITIVE = 0x00000004
AW_VER_NEGATIVE = 0x00000008

# These GW_ constants are used for GetWindow() and are documented at
# https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getwindow#parameters
GW_CHILD = 5
GW_ENABLEDPOPUP = 6
GW_HWNDFIRST = 0
GW_HWNDLAST = 1
GW_HWNDNEXT = 2
GW_HWNDPREV = 3
GW_OWNER = 4

# These WPF_ constants are used for GetWindowPlacement() and are documented at
# https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-tagwindowplacement#members
WPF_ASYNCWINDOWPLACEMENT = 0x0004
WPF_RESTORETOMAXIMIZED = 0x0002
WPF_SETMINPOSITION = 0x0001

# These LSFW_ constants are used for LockSetForegroundWindow() and are
# documented at https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-locksetforegroundwindow
LSFW_LOCK = 1
LSFW_UNLOCK = 2

# These MB_ constants are used for MessageBox() and are documented at
# https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-messagebox#parameters
# Buttons in the dialog box:
MB_ABORTRETRYIGNORE = 0x00000002
MB_CANCELTRYCONTINUE = 0x00000006
MB_HELP = 0x00004000
MB_OK = 0x00000000
MB_OKCANCEL = 0x00000001
MB_RETRYCANCEL = 0x00000005
MB_YESNO = 0x00000004
MB_YESNOCANCEL = 0x00000003

# Icon to display:
MB_ICONEXCLAMATION =  MB_ICONWARNING = 0x00000030
MB_ICONINFORMATION = MB_ICONASTERISK = 0x00000040
MB_ICONQUESTION = 0x00000020
MB_ICONSTOP = MB_ICONERROR = MB_ICONHAND = 0x00000010

# Which button is default:
MB_DEFBUTTON1 = 0x00000000
MB_DEFBUTTON2 = 0x00000100
MB_DEFBUTTON3 = 0x00000200
MB_DEFBUTTON4 = 0x00000300

# Modality of the dialog box:
MB_APPLMODAL = 0x00000000
MB_SYSTEMMODAL = 0x00001000
MB_TASKMODAL = 0x00002000

# Other options:
MB_DEFAULT_DESKTOP_ONLY = 0x00020000
MB_RIGHT = 0x00080000
MB_RTLREADING = 0x00100000
MB_SETFOREGROUND = 0x00010000
MB_TOPMOST = 0x00040000
MB_SERVICE_NOTIFICATION = 0x00200000

# Response integers for each button type:
IDABORT = 3
IDCANCEL = 2
IDCONTINUE = 11
IDIGNORE = 5
IDNO = 7
IDOK = 1
IDRETRY = 4
IDTRYAGAIN = 10
IDYES = 6

# SetWindowPos constants:
HWND_BOTTOM = 1
HWND_TOP = 0
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_ASYNCWINDOWPOS = 0x4000
SWP_DEFERERASE = 0x2000
SWP_DRAWFRAME = 0x0020 # TODO - Is this a typo in the docs?
SWP_FRAMECHANGED = 0x0020 # TODO - Is this a typo in the docs?
SWP_HIDEWINDOW = 0x0080
SWP_NOACTIVATE = 0x0010
SWP_NOCOPYBITS = 0x0100
SWP_NOMOVE = 0x0002
SWP_NOOWNERZORDER = 0x0200
SWP_NOREDRAW = 0x0008
SWP_NOREPOSITION = 0x0200
SWP_NOSENDCHANGING = 0x0400
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040

# Values copied from winuser.h, since they seem to absent from the MS docs.
MONITOR_DEFAULTTONEAREST = 2 # Returns a handle to the display monitor that is nearest to the point.
MONITOR_DEFAULTTONULL = 0 # Returns NULL.
MONITOR_DEFAULTTOPRIMARY = 1 # Returns a handle to the primary display monitor.

