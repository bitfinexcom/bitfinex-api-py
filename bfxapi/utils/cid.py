import time

def generate_unique_cid(multiplier: int = 1000) -> int:
    return int(round(time.time() * multiplier))
