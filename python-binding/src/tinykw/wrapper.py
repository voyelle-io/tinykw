import ctypes
import platform
from pathlib import Path

_lib: ctypes.CDLL = None

def _load_library(language: str):
    global _lib
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
    
    _lib = ctypes.CDLL(str(lib_path))
    _lib.tkw_init.restype  = ctypes.c_int32
    _lib.tkw_init.argtypes = []

    _lib.tkw_add_keyword.restype  = ctypes.c_int32
    _lib.tkw_add_keyword.argtypes = [ctypes.POINTER(ctypes.c_uint8), 
                                    ctypes.c_uint8, 
                                    ctypes.POINTER(ctypes.c_uint32)]

    _lib.tkw_process_frame.restype  = ctypes.c_int32
    _lib.tkw_process_frame.argtypes = [ctypes.POINTER(ctypes.c_int16),
                                        ctypes.c_size_t]

    _lib.tkw_is_keyword_detected.restype  = ctypes.c_int32
    _lib.tkw_is_keyword_detected.argtypes = [ctypes.c_uint32, 
                                            ctypes.POINTER(ctypes.c_uint32)]

    _lib.tkw_clear_keyword_flag.restype  = ctypes.c_int32
    _lib.tkw_clear_keyword_flag.argtypes = [ctypes.c_uint32]

    _lib.tkw_status_string.restype = ctypes.c_char_p
    _lib.tkw_status_string.argtypes = [ctypes.c_int32]
    return


AUDIO_FRAME_SIZE = 480

class tkwError(RuntimeError):
    pass

def _check_status(status: int):
    if status != 0:
        msg = _lib.tkw_status_string(status)
        msg = msg.decode() if msg else f"Error code {status}"
        raise tkwError(msg)

def tkw_init(language: str) -> None:
    """
    Initialize or reset the library.

    This should be called before any other API function. Calling tkw_init() multiple times is allowed 
    and resets all internal state, including registered keywords and detection flags.
    """
    _load_library(language)
    status = _lib.tkw_init()
    _check_status(status)


def tkw_add_keyword(data: list[int] | bytes, detection_threshold: float = 0.5) -> int:
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
    status = _lib.tkw_add_keyword(c_data, 
                                   ctypes.c_uint8(detection_threshold), 
                                   ctypes.byref(out_id))
    _check_status(status)
    return out_id.value


def tkw_process_frame(waveform) -> None:
    """
    Processes one frame of 16-bit PCM audio sampled at 16 kHz.

    Args:
        waveform: int16 numpy array or list of length tinykw.AUDIO_FRAME_SIZE.
    """
    if len(waveform) != AUDIO_FRAME_SIZE:
        raise ValueError(
            f"waveform must have length {AUDIO_FRAME_SIZE}, got {len(waveform)}"
        )
    if hasattr(waveform, "ctypes"):
        ptr = waveform.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    else:
        arr = (ctypes.c_int16 * len(waveform))(*waveform)
        ptr = arr
    status = _lib.tkw_process_frame(ptr, len(waveform))
    _check_status(status)


def tkw_is_keyword_detected(keyword_id: int) -> bool:
    """
   Reads the detection flag for a specific keyword.

    Args:
        id: keyword assigned ID.

    Returns:
        True if detected, False otherwise.
        Detection remains set until cleared with tkw_clear_keyword_flag().
    """
    out = ctypes.c_uint32()
    status = _lib.tkw_is_keyword_detected(ctypes.c_uint32(keyword_id), ctypes.byref(out))
    _check_status(status)
    return bool(out.value)


def tkw_clear_keyword_flag(keyword_id: int) -> None:
    """
    Clear detection flag.

    Args:
        id: keyword id
    """
    status = _lib.tkw_clear_keyword_flag(ctypes.c_uint32(keyword_id))
    _check_status(status)