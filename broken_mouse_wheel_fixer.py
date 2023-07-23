import argparse
import atexit
import evdev
import logging
from evdev import InputDevice
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

    def add(self, new_event):
        self._events.append(new_event)
        if len(self._events) >= self._events_size:
            del self._events[0]

    def trend(self):
        return max(set(self._events), key=self._events.count)


class App:
    def __init__(self, events):
        self._device = None
        self._fake_device = None
        self._events = events

        def cleanup():
            self._fake_device.close()
            self._device.close()

        atexit.register(cleanup)

    @staticmethod
    def find_matching_device(device_name):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == device_name:
                return device.path
        return None

    def run(self, device_path):
        self._device = InputDevice(device_path)
        self._fake_device = evdev.UInput.from_device(self._device, name="FakeMouseFromBrokenMouseWheelFixer")

        while True:
            r, w, x = select([self._device], [], [])
            for event in self._device.read():
                if event.type == evdev.ecodes.EV_REL and event.code == evdev.ecodes.ABS_WHEEL:
                    self._events.add(event.value)
                    trend = self._events.trend()
                    if trend != event.value:
                        # counter-act bad event by doing an opposite event on the fake device
                        self._fake_device.write(event.type, event.code, -event.value)
                        self._fake_device.syn()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Broken Mouse Wheel Fixer')
    parser.add_argument('buffer_size', nargs='?', default=10, type=int)
    parser.add_argument('device', nargs='?', default='2.4G Mouse', type=str)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

    mouse_device_path = App.find_matching_device(args.device)
    if mouse_device_path is None:
        logging.error(f'Failed to get device path for {args.device}')
    else:
        app = App(RecentEvents(events_size=args.buffer_size))
        app.run(mouse_device_path)
