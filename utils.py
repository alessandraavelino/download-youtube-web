def converter(time):
    try:
        splitted_time = time.split(":")

        minutes = int(splitted_time[0])
        seconds = int(splitted_time[1])

        fixed_time = (minutes * 60) + seconds
    except ValueError:
        return 0

    return fixed_time
