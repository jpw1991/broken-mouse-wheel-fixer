from evdev import InputDevice, UInput
from select import select

device = InputDevice('/dev/input/event7')
ui = UInput()


# scrolling
# up:   event at 1683315447.814400, code 08, type 02, val 01
# down: event at 1683315448.778384, code 08, type 02, val -1

# pattern of bad behaviour:
# event at 1683315597.933651, code 08, type 02, val -1
# event at 1683315598.751648, code 08, type 02, val -1
# event at 1683315598.755643, code 08, type 02, val 02
# event at 1683315598.763645, code 08, type 02, val -1
# event at 1683315605.023694, code 08, type 02, val -1
# event at 1683315618.679808, code 08, type 02, val 01
# event at 1683315619.087800, code 08, type 02, val -1
# event at 1683315619.455801, code 08, type 02, val -1
# event at 1683315619.619826, code 08, type 02, val -1
# event at 1683315619.939804, code 08, type 02, val -1
# event at 1683315620.639809, code 08, type 02, val -1
# event at 1683315621.797821, code 08, type 02, val -1
# event at 1683315621.829816, code 08, type 02, val -1

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


if __name__ == '__main__':
    events = RecentEvents()
    while True:
        r, w, x = select([device], [], [])
        for event in device.read():
            if event.type == 2 and event.code == 8:
                events.add(event.value)
                trend = events.trend()
                if events.trend() != event.value:
                    print(f"Discarding event because {event.value} doesn't match trend {trend}", event)
                    # Simulate the event on the virtual input device to prevent it from reaching other programs
                    ui.write(event.type, event.code, event.value)
                else:
                    # Permit event to propagate to other programs
                    continue
