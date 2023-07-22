# Broken Mouse Wheel Fixer

Got a broken mousewheel that skips and jumps? This may fix it for you, as it has done so for me.

## Why?

People often ask me: Why don't you just get a new mouse? It's a fair question. I have my reasons:

- I don't want to. I like this awful mouse.
- You presume a new mouse is going to work. Why would it work any better? They all come from the same place.
- Unless you're buying a good mouse for big cash, it's probably going to skip and jump after a few months as well.
- This is easier. It doesn't matter how bad the mouse's scroll wheel becomes, this software will keep it in check.
- You can feel good about yourself by not contributing to e-waste.

## General

**Platforms supported:**
- Linux (specifically, Ubuntu, but should work anywhere since it relies on [evdev](https://en.wikipedia.org/wiki/Evdev)) and it needs to be run as root.
  - Should work on both [Wayland](https://en.wikipedia.org/wiki/Wayland_(protocol)) and [X11](https://en.wikipedia.org/wiki/X_Window_System), but who knows. I use Wayland and it seems fine. To determine what you're running, execute `echo $XDG_SESSION_TYPE`
- Windows

## Usage

For Windows user convenience: See releases for compiled exes made using PyInstaller.

### Linux

```sh
# make virtual environment
mkdir venv
python3 -m venv venv

# activate & install requirements
source venv/bin/activate
pip install -r requirements.txt

# run as root
chmod +x broken_mouse_wheel_fixer.sh
sudo ./broken_mouse_wheel_fixer.sh
```

### Windows

```
# make virtual environment
mkdir venv
python -m venv myenv

# activate and install requirements
venv\Scripts\activate.bat
pip install -r requirements_windows.txt

# run
python broken_mouse_wheel_fixer_windows.py
```

## Function/Mechanism

It works by:

- Listening to your mouse wheel events (via [evdev](https://en.wikipedia.org/wiki/Evdev))
- Establishing a trend; for example, when scrolling up:
  - 1
  - 1
  - 1
  - -1
  - 1
  - 1
- If the individual event doesn't match the overall pattern of events, like a random -1 in the example above, this is the mouse wheel jumping/skipping and this event is ignored.
- Events are ignored by:
  - **Linux:** creating a fake copy of your mouse and writing an opposite event to it - cancelling it out.
  - **Windows:** returning False to pywinhook.

## Debugging

### Linux

- Run broken mouse wheel fixer
- Open a terminal, and run `libinput debug-events` and you should see the fake mouse get registered. In my example it is `event25`: 

```shell
-event1   DEVICE_ADDED            Power Button                      seat0 default group1  cap:k
-event0   DEVICE_ADDED            Power Button                      seat0 default group2  cap:k
-event24  DEVICE_ADDED            HP OMEN Mindframe Prime           seat0 default group3  cap:k
-event2   DEVICE_ADDED            SEMICO USB Keyboard               seat0 default group4  cap:k
-event3   DEVICE_ADDED            SEMICO USB Keyboard Consumer Control seat0 default group4  cap:kp scroll-nat
-event4   DEVICE_ADDED            SEMICO USB Keyboard System Control seat0 default group4  cap:k
-event5   DEVICE_ADDED            SEMICO USB Keyboard               seat0 default group4  cap:k
-event7   DEVICE_ADDED            2.4G Mouse                        seat0 default group5  cap:p left scroll-nat scroll-button
-event8   DEVICE_ADDED            ASIX Electronics AX68004          seat0 default group6  cap:k
-event9   DEVICE_ADDED            ASIX Electronics AX68004          seat0 default group6  cap:p left scroll-nat scroll-button
-event10  DEVICE_ADDED            ASIX Electronics AX68004 System Control seat0 default group6  cap:k
-event11  DEVICE_ADDED            ASIX Electronics AX68004 Consumer Control seat0 default group6  cap:kp scroll-nat
-event12  DEVICE_ADDED            ASIX Electronics AX68004          seat0 default group6  cap:p left scroll-nat calib
-event13  DEVICE_ADDED            Eee PC WMI hotkeys                seat0 default group7  cap:k
-event25  DEVICE_ADDED            FakeMouseFromBrokenMouseWheelFixer seat0 default group8  cap:p left scroll-nat scroll-button
```

- Use the mouse wheel and read the events
- You should see the correction kicking in for the fake device periodically

```shell
event7   POINTER_SCROLL_WHEEL    +57.385s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
-event25  POINTER_SCROLL_WHEEL    +57.385s	vert -15.00/-120.0* horiz 0.00/0.0 (wheel)
-event7   POINTER_SCROLL_WHEEL    +57.397s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
-event25  POINTER_SCROLL_WHEEL    +57.397s	vert -15.00/-120.0* horiz 0.00/0.0 (wheel)
-event7   POINTER_SCROLL_WHEEL    +57.417s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
-event25  POINTER_SCROLL_WHEEL    +57.417s	vert -15.00/-120.0* horiz 0.00/0.0 (wheel)
-event7   POINTER_SCROLL_WHEEL    +57.441s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
-event25  POINTER_SCROLL_WHEEL    +57.441s	vert -15.00/-120.0* horiz 0.00/0.0 (wheel)
 event7   POINTER_SCROLL_WHEEL    +57.953s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
 event7   POINTER_SCROLL_WHEEL    +57.981s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
 event7   POINTER_SCROLL_WHEEL    +58.013s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
 event7   POINTER_SCROLL_WHEEL    +58.037s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
 event7   POINTER_SCROLL_WHEEL    +58.065s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
 event7   POINTER_SCROLL_WHEEL    +58.097s	vert 15.00/120.0* horiz 0.00/0.0 (wheel)
```

## Run as Service

If you're like me and want this running automatically every time you log on, you can do the following to set it up as a `systemd` service:

- Create file at `/etc/systemd/system/brokenmousewheelfixer.service` with the following contents (replace repository path):

```ini
[Unit]
Description=Broken Mouse Wheel Fixer

[Service]
WorkingDirectory=/path/to/broken-mouse-wheel-fixer/
ExecStart=/path/to/broken-mouse-wheel-fixer/broken_mouse_wheel_fixer.sh

[Install]
WantedBy=multi-user.target
```

- Start as service with sudo: `systemctl start brokenmousewheelfixer.service`

It should from then on start whenever you login.
