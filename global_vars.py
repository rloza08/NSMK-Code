import sys
import utils.auto_pmdb as auto_pmdb

log_verbose = False  # Only if error_stop is set
error_stop = False
force_yes = True
use_serials = False
serial_not_available_revert_clone = True

EOM = lambda : print("_"*48)

def fake_assert():
    """

    :rtype: object
    """
    sys.stdout.flush()
    if error_stop:
        assert(0)
    else:
        if log_verbose:
            assert(0)
        if auto_pmdb.init_pmdb_flag is False:
            print("init_pmdb error, turn on verbose log mode for details")
            exit(-1)


def fake_abort():
    sys.stdout.flush()
    if log_verbose:
        assert(0)
    else:
        exit(-1)
