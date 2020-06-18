def convert_unit(x, a="m", b="cm"):
    """
    Description:
        qsd
    Input: 
        x: float 
        a: str input unit
        b: str output unit
    Output:
        x: float 
    """
    space = {"m": 1.0, "cm": 1e-2, "mm": 1e-3, "um": 1e-6, "nm": 1e-9}
    time = {"s": 1.0, "cs": 1e-2, "ms": 1e-3, "us": 1e-6, "ns": 1e-9}
    weight = {"t": 1e3, "kg": 1.0, "g": 1e-3}

    if (a in space) and (b in space):
        return space[a] / space[b] * x
    elif (a in time) and (b in time):
        return time[a] / time[b] * x
    elif (a in weight) and (b in weight):
        return weight[a] / weight[b] * x
