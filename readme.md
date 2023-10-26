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

- [Rotary encoders]https://thepihut.com/products/rotary-encoder-extras?variant=27740417681)
- [Motor controllers](https://thepihut.com/products/adafruit-dc-stepper-motor-hat-for-raspberry-pi-mini-kit?variant=27739845393)
- [Stepper motors](https://thepihut.com/products/stepper-motor-nema-17-size-200-steps-rev-12v-350ma?variant=27740390929)

## Logic

