def duration_str(start_time, end_time):
    seconds = end_time - start_time 
    minutes = int(seconds) // 60
    seconds = seconds - (minutes * 60)
    if minutes == 0:
        return '{:0.2f} seconds'.format(seconds)    
    return '{:d} minutes {:.0f} seconds'.format(minutes, seconds)