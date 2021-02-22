def htimeToSeconds(ht):
    """ Convert an human readable time string to seconds """
    if ht[-1] == 'm':
        return int(ht[0::-1]) * 60
    elif ht[-1] == 's':
        return int(ht[0::-1])
    elif ht[-1] == 'h':
        return int(ht[0::-1]) * 60 * 60
    elif ht[-1] == 'd':
        return int(ht[0::-1]) * 60 * 60 * 24
    else:
        return int(ht)