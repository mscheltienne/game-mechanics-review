INTERVENTION_TYPE_COLORS: dict[str, str] = {
    "Physical game": "#9bf6ff",
    "Cognitive training": "#bdb2ff",
    "Distraction": "#ffd6a5",
    "CBT": "#5ee3d3",
}
INTERVENTION_TYPE_ORDER: tuple[str] = (
    "Physical game",
    "Cognitive training",
    "Distraction",
    "CBT",
)

ENGAGEMENT_TYPE_COLORS: dict[str, str] = {
    "Affective": "#ffadad",
    "Cognitive": "#caffbf",
    "Behavioral": "#a0c4ff",
    "Socio-cultural": "#fdffb6",
}
ENGAGEMENT_TYPE_ORDER: tuple[str] = (
    "Affective",
    "Cognitive",
    "Behavioral",
    "Socio-cultural",
)

COLUMN_WIDTHS: tuple[float, float, float, float] = (0.14, 0.1, 0.3, 0.3)
COLUMNS_HEIGHTS: tuple[float, float] = (
    0.04,
    0.04,
)  # only defined for the first two columns

# common graphic properties
HPAD: float = 0.015
VPAD: float = 0.005

# sanity-check the constants
assert all(key in INTERVENTION_TYPE_COLORS for key in INTERVENTION_TYPE_ORDER), (
    "The order of the game mechanics is not consistent with the colors."
)
assert all(key in ENGAGEMENT_TYPE_COLORS for key in ENGAGEMENT_TYPE_ORDER), (
    "The order of the engagement types is not consistent with the colors."
)
