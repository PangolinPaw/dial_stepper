# Dial Input & Motor Control

## Components

```
Rotary encoders        Raspberry Pi           Motor controllers        Stepper motors

      ┌──┐                                   ┌──────────────────┐        ┌─────────┐
   ┌──┤  │         ┌──────────────────┐      │                  ├───────►│         │
   └──┤  ├───┐     │                  │      │                  │        │  ┌───┐  │
      └──┘   │     │                  ├─────►│                  │◄───────┤  │   │  │
             │     │                  │      │                  │        │  └───┘  │
      ┌──┐   │     │                  │◄─────┤                  ├────┐   │         │
   ┌──┤  │   │     │                  │      │                  │    │   └─────────┘
   └──┤  ├───┼────►│                  │      │                  │◄─┐ │
      └──┘   │     │                  │      └──────────────────┘  │ │   ┌─────────┐
             │     │                  │                            │ └──►│         │
      ┌──┐   │     │                  │                            │     │  ┌───┐  │
   ┌──┤  │   │     │                  │                            └─────┤  │   │  │
   └──┤  ├───┘     │                  │      ┌──────────────────┐        │  └───┘  │
      └──┘         │                  ├─────►│                  │        │         │
                   │                  │      │                  │        └─────────┘
                   │                  │◄─────┤                  │
                   └──────────────────┘      │                  │        ┌─────────┐
                                             │                  ├───────►│         │
                                             │                  │        │  ┌───┐  │
                                             │                  │◄───────┤  │   │  │
                                             └──────────────────┘        │  └───┘  │
                                                                         │         │
                                                                         └─────────┘
```

- [Rotary encoders](https://thepihut.com/products/rotary-encoder-extras?variant=27740417681)
- [Motor controllers](https://thepihut.com/products/adafruit-dc-stepper-motor-hat-for-raspberry-pi-mini-kit?variant=27739845393)
- [Stepper motors](https://thepihut.com/products/stepper-motor-nema-17-size-200-steps-rev-12v-350ma?variant=27740390929)

## Libraries & resources

- [Tracking the position of the rotary encoders](https://github.com/modmypi/Rotary-Encoder/blob/master/rotary_encoder.py)
- [Adafruit motor controller library](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/using-stepper-motors)

## Logic

- Dial turned X steps in Y direction
- Calculate new dial position P
- Covnert P to motor target position T
- Send signal to rotate motor in direction Y until T reached

## Things to consider

### Lag

There will be a lag between the dial turning & the motor reaching the corresponding position. This is especially true since the dial will have a fairly large diameter so the users will be able to spin the encoder quite far with minimal effort.

How should the system respond if the users move the dial to a new position before the motor has reached the previous target position?

Options:
1. Queue positions and move to each one in sequence
2. Cancel movement & start moving to new target position

**Updates:**

- Option 2 has been implemented, it's more intuitive and was simpler to code

### Dial to motor steps

The rotary encoders have 24 steps and the motors have 200. 1 step on the dial should therefore translate to 8 steps of the motors, leaving the last move before a full rotation a little longer than the others.

**Updates:**

- The dials are very senitive and it's hard to turn them in single-step incrememnts. It may actually be better to have more dial steps to motor steps than the originally planned 8
- Some 'smoothing' has been added so that the average of the last 3 signals from the dials is used to determine the motor movement

### Gear ratios

The disks mounted to the motors may be too heavy to rotate with a 1:1 ratio. A belt from the motor hub to the outer rim of the wheel could address this, but it would mean that the dial-to-motor step relationship would need to be adjusted.

**Updates:**

- The motor controller library offers an option to take "double steps" which allows for more torque. If the motor's struggle in the defaulst "single step" mode then this could be used instead. However, that may affect the dial-to-motor step ratio.

### Initial position

The rotary encoders and stepper motors can't report their positions, just when a step is taken and it's direction. This means that we must make sure the motors start in a known initial position when the machine is powered on. A physical lock of some sort might be a good way to ensure this.