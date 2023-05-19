import argparse
import datetime

from evdev import InputDevice, UInput, ecodes
from select import select


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


class RecentEventsLinux(RecentEvents):
    def __init__(self, events_size=10, logging_interval=10, device='/dev/input/event7'):
        super().__init__(events_size)
        self._device = InputDevice(device)
        self._ui = UInput()
        self._logging_interval = logging_interval
        self._next_log_at = datetime.datetime.now() + datetime.timedelta(minutes=logging_interval)
        self._scroll_up_blocked = 0
        self._scroll_down_blocked = 0
        self.Running = True
        self._handle_mouse_wheel_events()

    def __del__(self):
        self._ui.close()

    def add(self, x):
        super().add(x)
        if x >= 1:
            self._scroll_up_blocked += 1
        elif x <= -1:
            self._scroll_down_blocked += 1

    def _virtual_mouse_wheel_event(self, direction, scroll_amount=1):
        print(f'Generating virtual mouse wheel event for {direction}')

    def _handle_mouse_wheel_events(self):
        while self.Running:
            r, w, x = select([self._device], [], [])
            for event in self._device.read():
                if event.type == ecodes.EV_REL and event.code == ecodes.REL_WHEEL:
                    self.add(event.value)
                    trend = self.trend()
                    if self.trend() != event.value:
                        print(f"Discarding event because {event.value} doesn't match trend {trend}", event)
                        # Simulate the event on the virtual input device to prevent it from reaching other programs
                        self._ui.write(event.type, event.code, event.value)
                        self._ui.syn()

            now = datetime.datetime.now()
            if now > self._next_log_at:
                self._next_log_at = now + datetime.timedelta(minutes=self._logging_interval)
                print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}: '
                      f'Blocked a total of {self._scroll_up_blocked + self._scroll_down_blocked} mouse wheel up/down '
                      f'events ({self._scroll_up_blocked}/{self._scroll_down_blocked})')
                self.Running = False  # remove once production-ready


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Broken Mouse Wheel Fixer')
    parser.add_argument('buffer_size', nargs='?', default=10, type=int)
    parser.add_argument('logging_interval', nargs='?', default=1, type=int)
    parser.add_argument('device', nargs='?', default='/dev/input/event7', type=str)
    args = parser.parse_args()

    events = RecentEventsLinux(events_size=args.buffer_size,
                               logging_interval=args.logging_interval,
                               device=args.device)
