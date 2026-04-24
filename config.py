# config.py

# Game Constants
GRID_SIZE = 5
EMPTY = "."
WALL = "X"

# Room Coordinates (Simplified 5x5 Layout)
# (row, col)
ROOM_COORDINATES = {
    (0, 0): "Study",
    (0, 2): "Hall",
    (0, 4): "Lounge",
    (2, 0): "Library",
    (2, 2): "Billiard Room",
    (2, 4): "Dining Room",
    (4, 0): "Conservatory",
    (4, 2): "Ballroom",
    (4, 4): "Kitchen"
}

# Secret Passages: Start Room -> Target Room Coordinate
SECRET_PASSAGES = {
    "Study": (4, 4),        # To Kitchen
    "Kitchen": (0, 0),      # To Study
    "Conservatory": (0, 4), # To Lounge
    "Lounge": (4, 0)        # To Conservatory
}

# Data Lists
CHARACTERS = [
    "Miss Scarlett", "Colonel Mustard", "Mrs. White",
    "Reverend Green", "Mrs. Peacock", "Professor Plum"
]

WEAPONS = [
    "Candlestick", "Dagger", "Lead Pipe",
    "Revolver", "Rope", "Wrench"
]

ROOMS = list(ROOM_COORDINATES.values())

# Starting Positions
START_POSITIONS = {
    "Miss Scarlett": (0, 3),
    "Colonel Mustard": (1, 4),
    "Mrs. White": (4, 3),
    "Reverend Green": (4, 1),
    "Mrs. Peacock": (3, 0),
    "Professor Plum": (1, 0)
}