import ctypes
import ctypes.wintypes
path = r"D:\10days\ten-days-of-voice-agents-2025\backend\.venv\Lib\site-packages\onnxruntime\capi\onnxruntime.dll"
print('DLL path:', path)
handle = ctypes.windll.kernel32.LoadLibraryW(path)
if handle == 0:
    err = ctypes.windll.kernel32.GetLastError()
    print('LoadLibrary failed, GetLastError =', err)
    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.FormatMessageW(0x00001000, None, err, 0, buf, len(buf), None)
    print('Error message:', buf.value)
else:
    print('Loaded OK, handle =', handle)
    ctypes.windll.kernel32.FreeLibrary(handle)
