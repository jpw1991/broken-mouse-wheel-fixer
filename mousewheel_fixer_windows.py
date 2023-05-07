import pythoncom
import argparse
from pyWinhook import HookManager


class RecentEvents:
    def __init__(self, events_size=10):
        """
        When it comes to your specific situation, the events size is the most important variable to tweak. For my
        specific broken mouse, a value of 10 seems to work best.

        :param events_size:
        """
        self._events = []
        self._events_size = events_size

    def add(self, x):
        self._events.append(x)
        if len(self._events) >= self._events_size:
            del self._events[0]

    def trend(self):
        return max(set(self._events), key=self._events.count)


recent = RecentEvents()
quit_key_pressed = False


def on_mouse_event(event):
    global recent

    if event.Wheel == 0:
        return True  # pass event to other handlers

    recent.add(event.Wheel)
    # block by returning false if not matching trend
    permit_event = True

    trend = recent.trend()
    if trend != event.Wheel:
        print(f"Blocking input {event.Wheel} because it does not match trend of {trend}")
        permit_event = False

    return permit_event


def on_q_pressed(event):
    global quit_key_pressed

    if event.MessageName == 'key down' and event.Key == 'Q':
        quit_key_pressed = True
        return False  # consume event

    return True  # propagate event


if __name__ == '__main__':
    print('Starting...')

    parser = argparse.ArgumentParser()
    parser.add_argument('buffer_size', nargs='?', default=10, type=int)
    args = parser.parse_args()

    recent = RecentEvents(args.buffer_size)

    hm = HookManager()
    hm.MouseWheel = on_mouse_event
    hm.HookMouse()
    hm.KeyDown = on_q_pressed
    hm.HookKeyboard()
    print('Waiting for input. Press Q to quit!')
    while not quit_key_pressed:
        pythoncom.PumpWaitingMessages()
    print('Quitting...')
    hm.UnhookKeyboard()
    hm.UnhookMouse()
