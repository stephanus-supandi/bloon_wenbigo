"""
BOSSMEN WENBIGO - configuration v0.2
Every tunable gameplay parameter lives here. No magic numbers elsewhere.
All times are in SECONDS internally; milliseconds are display-only.
"""
GAME_TITLE    = "BOSSMEN WENBIGO"
GAME_SUBTITLE = "AI QUICK-DRAW DUEL"
VERSION       = "v0.2 - THE DUEL HAS SOUND"

# ---------------- Feature Toggles ----------------
AUDIO       = True    # Enable sound effects (falls back to terminal bell if no backend)
DIALOGUE    = True    # Enable character dialogue boxes
ANNOUNCER   = True    # Enable cinematic announcer text

# ---------------- Match rules ----------------
WINS_TO_TAKE_MATCH = 3
MAX_ROUNDS         = 9

# ---------------- Signal timing ----------------
DRAW_DELAY_MIN = 1.5
DRAW_DELAY_MAX = 4.0
TICK_INTERVAL  = 0.5

# ---------------- Pacing ----------------
SHOT_FLASH_HOLD = 0.35
RESULT_HOLD     = 3.5  # Slightly longer to read dialogue

# ---------------- Tie rule ----------------
TIE_TOLERANCE_MS = 5.0

# ---------------- False start ----------------
DOUBLE_FS_REPLAY = True

# ---------------- Performance labels ----------------
LABEL_INSANE_MAX_MS = 100.0
LABEL_FAST_MAX_MS   = 130.0
LABEL_NORMAL_MAX_MS = 170.0

# ---------------- AI personalities ----------------
BLOON = {
    "name":             "BLOON",
    "tagline":          "fast but wild",
    "base_rt":          0.135,
    "variance":         0.025,
    "false_start_prob": 0.02,
    "lapse_chance":     0.12,
    "lapse_range":      (0.030, 0.090),
    "rt_clamp":         (0.085, 0.350),
}

QWENY = {
    "name":             "QWENY",
    "tagline":          "slow but steady",
    "base_rt":          0.125,
    "variance":         0.010,
    "false_start_prob": 0.01,
    "lapse_chance":     0.05,
    "lapse_range":      (0.020, 0.060),
    "rt_clamp":         (0.090, 0.280),
}