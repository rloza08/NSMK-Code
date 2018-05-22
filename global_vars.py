import sys

log_verbose = True  # Only if error_stop is set
error_stop = False
force_yes = True
use_serials = False
serial_not_available_revert_clone = True

EOM = lambda : print("_"*48)

def fake_assert():
    sys.stdout.flush()
    if error_stop:
        if log_verbose:
            assert(0)
        else:
            exit(-1)
    else:
        pass

def fake_abort():
    sys.stdout.flush()
    if log_verbose:
        assert(0)
    else:
        exit(-1)
