# Falcon 3D Air Race

This is the upgraded version of the Python flight simulator.

The player aircraft is **FALCON**.  
The rival racing aircraft is **VIPER**.

It is a 3D-style air racing game made with Python and `pygame`.

## New features

- 3D-style camera and perspective projection
- Player aircraft: **FALCON**
- Rival aircraft: **VIPER**
- Air race checkpoint rings
- Race position tracking
- Radar/minimap
- Better flight physics:
  - throttle
  - thrust
  - drag
  - lift
  - gravity
  - stall warning
  - angle of attack
  - vertical speed
  - roll-based turning
  - ground effect
  - turbulence
  - terrain collision
- 3D terrain, mountains, runways, clouds, trees, towers, checkpoint rings, particles, and engine flame

---

# How to run this on a MacBook, explained for a total beginner

## Step 1: Download the game file

Download:

```text
falcon_3d_air_race.py
```

Most likely, your Mac will save it in the **Downloads** folder.

---

## Step 2: Open Terminal

Terminal is the app that lets you tell the computer to run the game.

Press:

```text
Command + Space
```

Type:

```text
Terminal
```

Press:

```text
Enter
```

A window will open. That is Terminal.

---

## Step 3: Install pygame

The game needs a Python game library called `pygame`.

Copy this command:

```bash
python3 -m pip install pygame
```

Paste it into Terminal.

Press:

```text
Enter
```

Wait until it finishes.

---

## Step 4: Go to your Downloads folder

In Terminal, type:

```bash
cd Downloads
```

Press:

```text
Enter
```

This tells Terminal: “go to the Downloads folder.”

---

## Step 5: Run the game

Now type:

```bash
python3 falcon_3d_air_race.py
```

Press:

```text
Enter
```

The game window should open.

---

# Controls

| Key | What it does |
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

# Goal of the game

You control **FALCON**.

Your rival is **VIPER**.

Fly through every glowing checkpoint ring before VIPER finishes the race.

Avoid mountains and terrain.

Do not stall.

Do not hit the ground.

---

# What does “stall” mean?

A stall means the aircraft is not getting enough lift.

In the game, stall can happen if:

- You fly too slowly
- You pitch the nose too high
- You climb too aggressively
- You lose too much speed during turns

If you see **STALL**, push the nose down slightly and increase throttle.

---

# If the game does not run

## If Terminal says `pygame` not found

Run:

```bash
python3 -m pip install pygame
```

Then run the game again:

```bash
python3 falcon_3d_air_race.py
```

## If Terminal says `No such file or directory`

It means Terminal is not inside the folder where the game file is.

Try:

```bash
cd Downloads
python3 falcon_3d_air_race.py
```

If you moved the file to Desktop, try:

```bash
cd Desktop
python3 falcon_3d_air_race.py
```

## If Terminal says `python3: command not found`

Python is not installed on your Mac.

Install Python first, then try again.

---

# Simple summary

1. Download `falcon_3d_air_race.py`
2. Open Terminal
3. Type `python3 -m pip install pygame`
4. Type `cd Downloads`
5. Type `python3 falcon_3d_air_race.py`
