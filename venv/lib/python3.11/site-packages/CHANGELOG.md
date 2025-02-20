# Changelog

0.0.5
-----

* Add support for int type in get_pin

0.0.4
-----

* Gracefully handle a tuple being passed to get_pin
* Match all pinctrl- gpiodevices for RPi in get_gpiochip_labels

0.0.3
-----

* Deprecate the `friendly_errors` flag in favour of a new `fatal` flag on methods
* Catch use of `int` pin numbers from unported code and raise a friendly error

0.0.2
-----

* Add platform detection
* ROCK 5B support
* Bug fixes

0.0.1
-----

* Initial Release
