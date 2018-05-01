import sys
global log_verbose
log_verbose = False  # Only if error_stop is set
error_stop = False
force_yes = False
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
