# rosflight_joy

These nodes use pygame to directly access the joysticks with python, and automatically detects the joystick type and mappings.  You'll need to install pygame to get them working

``` bash
sudo pip install pygame
```

Or whatever environment you're using.

There is a rosflight_joy_base class which does the auto-detection.  The other nodes create objects which inherit from this base class, but change the way the inputs are interpreted and which message is ultimately sent out.  Just change which node you are running to change modes.
