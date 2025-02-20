# gpiodevice

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/gpiodevice-python/test.yml?branch=main)](https://github.com/pimoroni/gpiodevice-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/gpiodevice-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/gpiodevice-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/gpiodevice.svg)](https://pypi.python.org/pypi/gpiodevice)
[![Python Versions](https://img.shields.io/pypi/pyversions/gpiodevice.svg)](https://pypi.python.org/pypi/gpiodevice)

A GPIO counterpart to [i2cdevice](https://github.com/pimoroni/i2cdevice-python), generated from [the Pimoroni Python Boilerplate](https://github.com/pimoroni/boilerplate-python).

## What is gpiodevice?

gpiodevice is a simple middleware library intended to make some user-facing aspects of interfacing with Linux's GPIO character device ABI (via gpiod) simpler and friendlier.

gpiodevice is not intended to replace gpiod, but collects some common patterns into a reusable library for GPIO-based Python projects.

