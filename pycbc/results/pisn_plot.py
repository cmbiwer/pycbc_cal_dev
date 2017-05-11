import matplotlib as mpl
from pycbc import pisn

snr_low = 0
snr_high = 40

def set_pisn_rcparams():
    rcParams = {
        "text.usetex": True,
        "figure.dpi": 600,
        "font.size": 10,
        "figure.figsize": (3.375, 2.5),
        "axes.titlesize": 10,
        "axes.labelsize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
    }
    mpl.rcParams.update(rcParams)

def in_region(low, high, region, parameter, current_parameter):
    """ Returns True if low and high are inside region. Else False.
    """

    if parameter != current_parameter:
        return False

    # in gap
    if region == "inside" and low > pisn.pisn_low and high < pisn.pisn_high:
        return True
    elif region == "inside":
        return False

    # below gap
    if region == "low" and high < pisn.pisn_low:
        return True
    elif region == "low":
        return False

    # above gap
    if region == "high" and low > pisn.pisn_high:
        return True
    elif region == "high":
        return False

    return False

