# Broken Mouse Wheel Fixer

Got a broken mousewheel that skips and jumps? This may fix it for you, as it has done so for me.

## General

**Platforms supported:**
- Linux (specifically, Ubuntu, but should work anywhere since it relies on [evdev](https://en.wikipedia.org/wiki/Evdev)) and it needs to be run as root.
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
  - **Linux:** writing the event to a [virtual device](https://pypi.org/project/python-uinput/) thereby handling/consuming it
  - **Windows:** returning False to pywinhook

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
