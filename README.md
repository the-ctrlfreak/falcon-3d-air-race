[README.md](https://github.com/user-attachments/files/29469483/README.md)
Falcon 3D Air Race

**Falcon 3D Air Race** is a colourful 3D-style Python flight racing game built with `pygame`.

You fly the aircraft **FALCON** against a rival aircraft called **VIPER**.  
Your mission is to race through glowing checkpoint rings, avoid terrain, manage speed and throttle, and reach the finish before VIPER.

Features

- 3D-style chase camera using projection math
- Player aircraft: **FALCON**
- Rival aircraft: **VIPER**
- Air racing checkpoint system
- Race position tracking
- Radar / minimap
- Terrain collision
- Runways, mountains, clouds, trees, towers, and glowing rings
- Engine flame and particle effects
- Flight HUD showing:
  - Airspeed
  - Altitude
  - AGL height
  - Vertical speed
  - Pitch
  - Roll
  - Heading
  - Angle of attack
  - Fuel
  - Airframe health
- More advanced arcade flight physics:
  - Thrust
  - Drag
  - Lift
  - Gravity
  - Stall warning
  - Ground effect
  - Turbulence
  - Roll-based turning

Requirements

You need:

- Python 3
- pygame

Install pygame with:

```bash
python3 -m pip install pygame
```

---

How to Run on MacBook

 1. Download or clone this repository

If you downloaded the file manually, make sure `falcon_3d_air_race.py` is in your **Downloads** folder or project folder.

2. Open Terminal

Press:

```text
Command + Space
```

Type:

```text
Terminal
```

Press **Enter**.

 3. Install pygame

```bash
python3 -m pip install pygame
```

4. Go to the folder where the game is saved

If the file is in Downloads:

```bash
cd Downloads
```

If the file is on Desktop:

```bash
cd Desktop
```

### 5. Run the game

```bash
python3 falcon_3d_air_race.py
```

The game window should open.

---

 Controls

| Key | Action |
|---|---|
| W / Up Arrow | Pitch up |
| S / Down Arrow | Pitch down |
| A / Left Arrow | Roll left |
| D / Right Arrow | Roll right |
| Q | Rudder yaw left |
| E | Rudder yaw right |
| Shift | Increase throttle |
| Ctrl | Decrease throttle |
| Space | Auto-level aircraft |
| V | Change camera distance |
| H | Show/hide help |
| R | Restart after crash or finish |
| Esc | Quit |

---

Goal

Fly **FALCON** through every glowing checkpoint ring before **VIPER** finishes the race.

Avoid:

- Crashing into terrain
- Flying too low
- Stalling
- Losing too much speed in sharp turns

---

Flight Tips

Avoid stalls

A stall happens when the aircraft loses lift.

In this game, stalls can happen if:

- You fly too slowly
- You pitch up too much
- You climb too aggressively
- You turn hard while losing speed

To recover:

1. Push the nose down slightly.
2. Increase throttle.
3. Level the wings.
4. Build speed again.

Avoid terrain crashes

If you see a terrain warning, climb or turn away quickly.

Win the race

Try to take smooth turns through the checkpoints instead of making sharp last-second movements.

---

Troubleshooting

pygame not found

Run:

```bash
python3 -m pip install pygame
```

Then try again:

```bash
python3 falcon_3d_air_race.py
```

 No such file or directory

You are probably not inside the folder where the game file is saved.

Try:

```bash
cd Downloads
python3 falcon_3d_air_race.py
```

Or, if the file is on Desktop:

```bash
cd Desktop
python3 falcon_3d_air_race.py
```

 python3 command not found

Python is not installed on your Mac.

Install Python 3, then try again.

Project Files

Recommended repository structure:

```text
falcon-3d-air-race/
├── falcon_3d_air_race.py
├── README.md

Future Improvements

Possible future upgrades:

- Real 3D engine version
- Sound effects
- Main menu
- Aircraft selection
- Multiple race tracks
- Better AI opponent
- Multiplayer mode
- Keyboard and controller support
- Landing challenges
- Missions and campaign mode

License

This project is free to use and modify.

You can add an official license later, such as the MIT License, if you want to share it publicly on GitHub.
