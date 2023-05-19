import argparse
import datetime

import Xlib.protocol
from Xlib import X, display
from Xlib.ext import xtest


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
        # return sum(self._events)
        return max(set(self._events), key=self._events.count)


class RecentEventsX(RecentEvents):
    SCROLL_UP = 4
    SCROLL_DOWN = 5
    VIRTUAL_MOUSE_WHEEL_EVENT_TYPE = 33

    def __init__(self, events_size=10, logging_interval=10):
        super().__init__(events_size)

        self._display = display.Display()
        self._root = self._display.screen().root

        self._logging_interval = logging_interval
        self._next_log_at = datetime.datetime.now() + datetime.timedelta(minutes=logging_interval)
        self._scroll_up_blocked = 0
        self._scroll_down_blocked = 0

        self.Running = True

        self._handle_mouse_wheel_events()

    def __del__(self):
        self._display.close()

    def add(self, x):
        super().add(x)
        if x >= 1:
            self._scroll_up_blocked += 1
        elif x <= -1:
            self._scroll_down_blocked += 1

    def _block_mouse_wheel_event(self, direction):
        # ButtonPress(type = 4, detail = 4, sequence_number = 902, time = 48116429, root = <Window 0x000001e6>, window = <Window 0x000001e6>, child = <Window 0x0260003d>, root_x = 1036, root_y = 450, event_x = 1036, event_y = 450, state = 16, same_screen = 1)
        value = 1 if direction == self.SCROLL_UP else -1
        self.add(value)
        return self.trend() != value

    def _virtual_mouse_wheel_event(self, direction):
        print(f'Generating virtual mouse wheel event for {direction}')
        # if direction == self.SCROLL_UP:
        #     self._ui.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_WHEEL, 1)   # Scroll the wheel up
        #     self._ui.write(evdev.ecodes.EV_SYN, evdev.ecodes.SYN_REPORT, 0)  # Send a synchronization event
        # else:
        #     self._ui.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_WHEEL, -1)  # Scroll the wheel down
        #     self._ui.write(evdev.ecodes.EV_SYN, evdev.ecodes.SYN_REPORT, 0)  # Send a synchronization event
        # fake input works well but is indistinguishable from real input and so triggers an endless event loop
        xtest.fake_input(self._display, X.ButtonPress, direction, root=self._root)
        xtest.fake_input(self._display, X.ButtonRelease, direction, root=self._root)
        # self._root.send_event(Xlib.protocol.event.ButtonPress(
        #     time=X.CurrentTime,
        #     root=self._root,
        #     same_screen=True,
        #     window=self._root,
        #     child=X.NONE,
        #     root_x=X.NONE,
        #     root_y=X.NONE,
        #     event_x=X.NONE,
        #     event_y=X.NONE,
        #     state=X.NONE,
        #     send_event=True,  # Set the send_event attribute to True to mark it as synthetic
        #     detail=direction
        # ))
        # self._root.send_event(Xlib.protocol.event.ButtonRelease(
        #     time=X.CurrentTime,
        #     root=self._root,
        #     same_screen=True,
        #     window=self._root,
        #     child=X.NONE,
        #     root_x=X.NONE,
        #     root_y=X.NONE,
        #     event_x=X.NONE,
        #     event_y=X.NONE,
        #     state=X.NONE,
        #     send_event=True,  # Set the send_event attribute to True to mark it as synthetic
        #     detail=direction
        # ))

    def _disable_mouse_wheel_input(self):
        self._root.grab_button(
            button=self.SCROLL_UP,
            modifiers=X.AnyModifier,
            owner_events=True,
            event_mask=X.ButtonPressMask,
            pointer_mode=X.GrabModeAsync,
            keyboard_mode=X.GrabModeAsync,
            confine_to=X.NONE,
            cursor=X.NONE
        )
        self._root.grab_button(
            button=self.SCROLL_DOWN,
            modifiers=X.AnyModifier,
            owner_events=True,
            event_mask=X.ButtonPressMask,
            pointer_mode=X.GrabModeAsync,
            keyboard_mode=X.GrabModeAsync,
            confine_to=X.NONE,
            cursor=X.NONE
        )

    def _enable_mouse_wheel_input(self):
        self._root.ungrab_button(self.SCROLL_UP, X.AnyModifier)
        self._root.ungrab_button(self.SCROLL_DOWN, X.AnyModifier)

    def _handle_mouse_wheel_events(self):

        # tell X we're only interested in button presses and not other events
        self._root.change_attributes(event_mask=X.ButtonPressMask | X.ButtonReleaseMask)

        self._disable_mouse_wheel_input()

        ignore_sequence_numbers = []
        while self.Running:
            event = self._root.display.next_event()
            print(event)
            if event.sequence_number in ignore_sequence_numbers:
                print(f'Skipping {event.sequence_number}')
                continue
            # if event.send_event:
            #     print('Skipping synthetic event')
            #     continue  # skip synthetic events
            if event.type in (X.ButtonPress, X.ButtonRelease):
                # check if input needs to be blocked
                block_input = self._block_mouse_wheel_event(event.detail)
                if not block_input:
                #     self._enable_mouse_wheel_input()
                # else:
                #     self._disable_mouse_wheel_input()
                    # ignore the next 2 sequence numbers (they will be the mouse wheels we generate)
                    # and these seem to be increments of 4
                    ignore_sequence_numbers = [event.sequence_number + 4, event.sequence_number + 8]
                    # perform a mouse up/down on the virtual mouse
                    self._virtual_mouse_wheel_event(event.detail)

            self._display.allow_events(X.ReplayPointer, X.CurrentTime)
            self._display.sync()

            now = datetime.datetime.now()
            if now > self._next_log_at:
                self._next_log_at = now + datetime.timedelta(minutes=self._logging_interval)
                print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}: '
                      f'Blocked a total of {self._scroll_up_blocked + self._scroll_down_blocked} mouse wheel up/down '
                      f'events ({self._scroll_up_blocked}/{self._scroll_down_blocked})')
                self.Running = False

        self._enable_mouse_wheel_input()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Broken Mouse Wheel Fixer')
    parser.add_argument('buffer_size', nargs='?', default=10, type=int)
    parser.add_argument('logging_interval', nargs='?', default=1, type=int)
    parser.add_argument('device', nargs='?', default='/dev/input/event7', type=str)
    args = parser.parse_args()

    events = RecentEventsX(events_size=args.buffer_size,
                           logging_interval=args.logging_interval)
