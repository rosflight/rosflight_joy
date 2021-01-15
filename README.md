# rosflight_joy

These nodes use pygame to directly access the joysticks with python, and automatically detects the joystick type and mappings.  You'll need to install pygame to get them working

``` bash
pip install pygame
```

Or whatever environment you're using.

There is a rosflight_joy_base class which does the auto-detection.  The other nodes create objects which inherit from this base class, but change the way the inputs are interpreted and which message is ultimately sent out.  Just change which node you are running to change modes.

## rc_keyboard node

Another node is provided called `rc_keyboard` which mimics the functionality of a joystick device through pressing keys on a keyboard. It is intended to be a convenience node for those using the `rosflight_joy` package in simulation. It provides some basic functionality, but only allows for very coarse control - as one would expect when flying using keyboard presses.

### User instructions

First, press alt+TAB until `rc_keyboard` window is focused. Once focused, pressing the following keys will result in these commands:

- W/S = throttle up/down
- A/D = yaw left/right
- Up/Down = pitch forward/backward
- Left/Right = roll left/right
- M = arm toggle
- O = RC override toggle
- Z = set throttle to 100%
- X = set throttle to 0%
- C = set throttle to 50%

### Automatic arm and takeoff

`rc_keyboard` can optionally arm the aircraft automatically, as well as shift to full throttle after arming to allow for autonomous navigation to take over.

This node assumes that the RC channels are set to: `[ROLL, PITCH, THROTTLE, YAW, RC_OVERRIDE, ARM (or none), none, none]`. i.e., it assumes that the ROSflight parameters `RC_ATT_OVRD_CHN` and `RC_THR_OVRD_CHN` are set to channel 4, and `ARM_CHANNEL` is set to channel 5 (although this last one is optional). Note that the channel number is zero-indexed.

The node listens for the following ROS parameters:

Format: `param_name`: (type, default value) Description of what is published to `/RC` topic, where low = -1 (min value), high = 1 (max value), and neutral = 0 (middle value)
- `auto_arm`: (bool, false) if true,
  - low on `F` (channel 2, throttle)
  - high on `z` (channel 3, yaw) <-- in case `ARM_CHANNEL` is not set
  - high on `aux1` (channel 4, RC override)
  - high on `aux2` (channel 5, arm toggle)
  - publish these until `/status` reports `armed: true`, after which publish low on `aux1` (RC override) and neutral to `z` (yaw)
- `auto_takeoff`: (bool, false) if true AND `auto_arm` is true,
  - high on `F` (channel 2, throttle) after successful arm

The node waits for an incoming message on the `/version` topic before publishing anything.