def _reduce_das_on_dmard(current_treatments, das_score):
    if 'dmard' in current_treatments:
        das_score = das_score * 0.9
        return das_score
    else:
        return das_score

def _increase_das_on_flare(flare_time, das_score):
    if flare_time == 1:
        das_score = das_score * 1.1
        return das_score
    else:
        return das_score

