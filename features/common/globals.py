import threading

_tts_working =False
_recording_requested = False
_lock = threading.Lock()


def set_tts_state(state):
    global _tts_working
    with _lock:
        _tts_working = state

def is_tts_working():
    with _lock:
        return _tts_working

def set_recording_requested(state):
    global _recording_requested
    with _lock:
        _recording_requested =state

def is_recording_requested():
    global _recording_requested
    with _lock:
        return _recording_requested