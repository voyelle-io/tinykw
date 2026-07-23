import ctypes
import platform
from pathlib import Path

_libs: dict[str, ctypes.CDLL] = {}

def _load_library(language: str) -> ctypes.CDLL:
    global _libs
    if language in _libs:
        return _libs[language]

    system = platform.system()
    machine = platform.machine()
    arch = {
        "x86_64": "x86_64",
        "AMD64": "x86_64",   
        "arm64": "arm64",
        "ARM64": "arm64",
        "aarch64": "arm64",
    }.get(machine)

    if arch is None:
        raise OSError(f"Unsupported architecture: {machine}")

    lib_dir = Path(__file__).parent / "libs" / language
    if system == "Darwin":
        lib_path = lib_dir / "libtinykw.dylib"
    elif system == "Linux":
        lib_path = lib_dir / "libtinykw.so"
    elif system == "Windows":
        lib_path = lib_dir / "libtinykw.dll"
    else:
        raise OSError(f"Unsupported platform: {system}")

    if not lib_path.exists():
        suported_languages = [x.name for x in (Path(__file__).parent / "libs").iterdir() if x.is_dir()]
        raise OSError(f"Language '{language}' is not supported. Supported languages are {suported_languages}")
    
    lib = ctypes.CDLL(str(lib_path))

    lib.tkw_create.argtypes = []
    lib.tkw_create.restype  = ctypes.c_void_p

    lib.tkw_destroy.argtypes = [ctypes.c_void_p]
    lib.tkw_destroy.restype  = None

    lib.tkw_add_keyword.argtypes = [ctypes.POINTER(ctypes.c_uint8), 
                                    ctypes.c_uint8, 
                                    ctypes.POINTER(ctypes.c_uint32),
                                    ctypes.c_void_p]
    lib.tkw_add_keyword.restype  = ctypes.c_int32

    lib.tkw_process_frame.argtypes = [ctypes.POINTER(ctypes.c_int16),
                                        ctypes.c_size_t,
                                        ctypes.c_void_p]
    lib.tkw_process_frame.restype  = ctypes.c_int32

    lib.tkw_is_keyword_detected.argtypes = [ctypes.c_uint32, 
                                            ctypes.POINTER(ctypes.c_uint32),
                                            ctypes.c_void_p]
    lib.tkw_is_keyword_detected.restype  = ctypes.c_int32

    lib.tkw_clear_keyword_flag.argtypes = [ctypes.c_uint32, 
                                            ctypes.c_void_p]
    lib.tkw_clear_keyword_flag.restype  = ctypes.c_int32

    lib.tkw_status_string.argtypes = [ctypes.c_int32]
    lib.tkw_status_string.restype = ctypes.c_char_p

    _libs[language] = lib
    return _libs[language]


AUDIO_FRAME_SIZE = 480

class tkwError(RuntimeError):
    pass

class TkwEngine:
    def __init__(self, language):
        self._lib = _load_library(language)
        self._ctx = self._lib.tkw_create()
        if not self._ctx:
            raise MemoryError("tkw_create failed")
        self.frame_size = AUDIO_FRAME_SIZE
    
    def add_keyword(self, data: list[int] | bytes, detection_threshold: float = 0.5) -> int:
        """
        Adds a keyword to the engine.

        Args:
            data: 48 bytes keyword encoding (can be obtained from https://voyelle.io/tinykw).
            detection_threshold: value between 0 and 1. 
                Controls how strict the engine is when deciding whether a detection is valid.
                A high value makes the engine more conservative: only high-scoring detections are accepted (fewer false positives, but more missed detections).
                A low value makes the engine more permissive: more detections are accepted (fewer misses, but more false positives).
                This parameter may need tuning depending on the keyword, use case and environment. A good starting point is to set it mid-range at 0.5, and 
                then eventually adjust it based on your tolerance for false positives vs missed detections.
        
        Returns:
            id: the assigned keyword ID

        Example:
            data = [0x3f, 0x12, 0x00, ...]  # 48 bytes
            id = tkw_add_keyword(data, 0.75)
        """
        if isinstance(data, bytes):
            data = list(data)
        if len(data) != 48:
            raise ValueError(f"data must be exactly 48 bytes, got {len(data)}")
        if not (0.0 <= detection_threshold <= 1.0):
            raise ValueError("detection_threshold must be in [0.0, 1.0]")
        detection_threshold = max(0, min(255, round(detection_threshold * 256)))
        c_data = (ctypes.c_uint8 * 48)(*data)
        out_id = ctypes.c_uint32()
        status = self._lib.tkw_add_keyword(c_data, 
                                    ctypes.c_uint8(detection_threshold), 
                                    ctypes.byref(out_id), 
                                    self._ctx)
        self._check_status(status)
        return out_id.value
    
    def process_frame(self, waveform) -> None:
        """
        Processes one frame of 16-bit PCM audio sampled at 16 kHz.

        Args:
            waveform: int16 numpy array or list of length self.frame_size.
        """
        if len(waveform) != self.frame_size:
            raise ValueError(
                f"waveform must have length {self.frame_size}, got {len(waveform)}"
            )
        if hasattr(waveform, "ctypes"):
            ptr = waveform.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        else:
            arr = (ctypes.c_int16 * len(waveform))(*waveform)
            ptr = arr
        status = self._lib.tkw_process_frame(ptr, len(waveform), self._ctx)
        self._check_status(status)

    def is_keyword_detected(self, keyword_id: int) -> bool:
        """
        Reads the detection flag for a specific keyword.

        Args:
            id: keyword assigned ID.

        Returns:
            True if detected, False otherwise.
            Detection remains set until cleared with tkw_clear_keyword_flag().
        """
        out = ctypes.c_uint32()
        status = self._lib.tkw_is_keyword_detected(ctypes.c_uint32(keyword_id), ctypes.byref(out), self._ctx)
        self._check_status(status)
        return bool(out.value)

    def clear_keyword_flag(self, keyword_id: int) -> None:
        """
        Clear detection flag.

        Args:
            id: keyword id
        """
        status = self._lib.tkw_clear_keyword_flag(ctypes.c_uint32(keyword_id), self._ctx)
        self._check_status(status)

    def _check_status(self, status: int):
        if status != 0:
            msg = self._lib.tkw_status_string(status)
            msg = msg.decode() if msg else f"Error code {status}"
            raise tkwError(msg)
        
    def close(self):
        ctx = getattr(self, '_ctx', None)
        if ctx:
            self._lib.tkw_destroy(self._ctx)

    def __del__(self):
        self.close()
