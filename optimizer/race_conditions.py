def apply_safety_adjustment(lap_time, event):
    if event == "SC":
        return lap_time * 0.5
    if event == "VSC":
        return lap_time * 0.7
    return lap_time

def pit_loss(base_loss, event):
    if event == "SC":
        return base_loss * 0.45
    if event == "VSC":
        return base_loss * 0.6
    return base_loss
