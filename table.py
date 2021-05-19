"""copied tables and hardcoded values"""

# title, description, value
DV = [
    [
        "Simple",
        "This is something most people can do without thinking, but which might be hard for a small child.",
        9,
    ],
    [
        "Everyday",
        "This feat is something most people can do without a lot of special training.",
        13,
    ],
    [
        "Difficult",
        "This feat is difficult to accomplish without training or natural talent.",
        15,
    ],
    [
        "Professional",
        "This feat takes actual training and the user can be considered to be a professional, skilled in their abilities.",
        17,
    ],
    [
        "Heroic",
        "This is a highly skilled feat; one that only the best of the best can pull off. This is the level of sports stars and other highly regarded superstars.",
        21,
    ],
    [
        "Incredible",
        "This is a tremendous feat. Pulling this off would rate you among the very best of your class professionally. You are of truly Olympian mettle.",
        24,
    ],
    [
        "Legendary",
        "An awe-inspiring feat. This is something people write stories about; a truly amazing accomplishment that will be spoken of in hushed tones for years to come.",
        29,
    ],
]

# description, value
MODIFIERS = [
    ["Complimentary skill", 1],
    ["Taking extra time", 1],
    ["With luck", 1],
    ["Night or low lighting conditions", -1],
    ["Have never done this before", -1],
    ["Complex task", -2],
    ["Don't have right tools or parts", -2],
    ["Slept uncomfortable the night before.", -2],
    ["Under extreme stress", -2],
    ["Exhausted", -4],
    ["Extremely drunk or sedated", -4],
    ["Trying to perform task secretly", -4],
    ["Task obscured by smoke, darkness", -4],
]
