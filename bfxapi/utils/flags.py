from .. enums import Flag

def calculate_order_flags(
    hidden : bool = False,
    close : bool = False,
    reduce_only : bool = False,
    post_only : bool = False,
    oco : bool = False,
    no_var_rates: bool = False
) -> int:
    flags = 0

    if hidden: flags += Flag.HIDDEN
    if close: flags += Flag.CLOSE
    if reduce_only: flags += Flag.REDUCE_ONLY
    if post_only: flags += Flag.POST_ONLY
    if oco: flags += Flag.OCO
    if no_var_rates: flags += Flag.NO_VAR_RATES

    return flags

def calculate_offer_flags(
    hidden : bool = False
) -> int:
    flags = 0

    if hidden: flags += Flag.HIDDEN

    return flags