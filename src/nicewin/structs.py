import ctypes


class POINT(ctypes.Structure):
    """A nice wrapper of the POINT structure.

    "The POINT structure defines the x- and y- coordinates of a point."

    The POINT structure is used by GetCursorPos(), WindowFromPhysicalPoint(),
    and other functions.

    Syntax:

    typedef struct tagPOINT {
      LONG x;
      LONG y;
    } POINT, *PPOINT;

    Microsoft Documentation:
    http://msdn.microsoft.com/en-us/library/windows/desktop/dd162805(v=vs.85).aspx
    """
    _fields_ = [('x', ctypes.c_long),
                ('y', ctypes.c_long)]

class RECT(ctypes.Structure):
    """A nice wrapper of the RECT structure.

    Syntax:
    typedef struct _RECT {
      LONG left;
      LONG top;
      LONG right;
      LONG bottom;
    } RECT, *PRECT;

    Microsoft Documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/dd162897(v=vs.85).aspx
    """
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]


class WINDOWPLACEMENT(ctypes.Structure):
    """A nice wrapper of the WINDOWPLACEMENT structure.

    Syntax:
    typedef struct tagWINDOWPLACEMENT {
      UINT  length;
      UINT  flags;
      UINT  showCmd;
      POINT ptMinPosition;
      POINT ptMaxPosition;
      RECT  rcNormalPosition;
      RECT  rcDevice;
    } WINDOWPLACEMENT;

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-tagwindowplacement
    """
    _fields_ = [('length', ctypes.c_uint),
                ('flags', ctypes.c_uint),
                ('showCmd', ctypes.c_uint),
                ('ptMinPosition', POINT),
                ('ptMaxPosition', POINT),
                ('rcNormalPosition', RECT),
                ('rcDevice', RECT)]

