import time
from datetime import datetime, timedelta


def progress_bar(start_time, idx, total_items):
    elapsed_time = time.time() - start_time
    remaining_time = (total_items - idx) * (elapsed_time / idx)
    hours, remainder = divmod(int(remaining_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    progress = int((idx / total_items) * 50)
    bar = "=" * (progress - 1) + "|" + "." * (50 - progress)
    end_time = datetime.now() + timedelta(seconds=remaining_time)
    end_time_str = end_time.strftime("%d-%m-%Y %H:%M:%S")
    return f"[{bar}]{idx * 100 // total_items}% | Falta:{hours:02}:{minutes:02}:{seconds:02} | Termina:{end_time_str}"
