import numpy as np
from sklearn.ensemble import RandomForestClassifier

# === Training Data ===
# Features: [motion, light, hour]
X = np.array([
    # unoccupied dark
    [0, 0, 1],
    [0, 3, 4],
    [0, 5, 23],

    # occupied dark (night)
    [1, 2, 0],
    [1, 1, 22],
    [1, 3, 2],

    # occupied dark (day)
    [1, 5, 10],
    [1, 4, 8],
    [1, 2, 18],
    
    # unoccupied dim
    [0, 6, 12],
    [0, 20, 7],
    [0, 25, 15],

    # occupied dim (day)
    [1, 15, 10],
    [1, 20, 14],
    [1, 24, 17],

    # occupied dim (night)
    [1, 10, 23],
    [1, 12, 1],
    [1, 18, 4],

    # unoccupied lit
    [0, 30, 12],
    [0, 50, 9],
    [0, 100, 16],

    # occupied lit (day)
    [1, 45, 13],
    [1, 70, 11],
    [1, 90, 17],

    # occupied lit (night)
    [1, 35, 21],
    [1, 60, 0],
    [1, 80, 3],
])

y = [
    "unoccupied dark",
    "unoccupied dark",
    "unoccupied dark",

    "occupied dark (night)",
    "occupied dark (night)",
    "occupied dark (night)",

    "occupied dark (day)",
    "occupied dark (day)",
    "occupied dark (day)",

    "unoccupied dim",
    "unoccupied dim",
    "unoccupied dim",

    "occupied dim (day)",
    "occupied dim (day)",
    "occupied dim (day)",

    "occupied dim (night)",
    "occupied dim (night)",
    "occupied dim (night)",

    "unoccupied lit",
    "unoccupied lit",
    "unoccupied lit",

    "occupied lit (day)",
    "occupied lit (day)",
    "occupied lit (day)",

    "occupied lit (night)",
    "occupied lit (night)",
    "occupied lit (night)"
]

# Train model
clf = RandomForestClassifier()
clf.fit(X, y)

# === Light Control Functions ===
def classify_scene(motion, light, hour):
    return clf.predict([[motion, light, hour]])[0]