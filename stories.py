# stories.py -- the world news of Thursday 19 November 2026, as reported that day.
# Every line below is baked into the repository: the program fetches nothing
# at run time. Facts were checked against the day's reporting (BBC, AP,
# Japan Times, Times of Israel, NDTV, Horizon, One Turn) on 19 Nov 2026.

DATE_LINE = "THURSDAY 19 NOVEMBER 2026"
MASTHEAD = "THE WORLD IN ONE DAY"

LEAD = {
    "kicker": "LEAD  •  DIPLOMACY",
    "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
    "body": (
        "The presidents of the United States, China and Russia hold their "
        "first three-way summit, on the APEC sidelines in Shenzhen. Trump "
        "meets Xi and Putin separately first; Ukraine and the Iran war top "
        "the agenda. Trump says the US and China both want Hormuz kept "
        "open and agree Iran must not get a nuclear weapon."
    ),
}

PANELS = [
    {
        "kicker": "JUSTICE  •  THE HAGUE",
        "headline": "Myanmar guilty of genocide",
        "body": (
            "The UN's top court rules Myanmar committed state-sponsored "
            "genocide against the Rohingya."
        ),
        "icon": "scales",
    },
    {
        "kicker": "WAR IN UKRAINE  •  CRIMEA",
        "headline": "Crimea bridge hit again",
        "body": (
            "Ukraine strikes the bridge to Crimea for the third time in a "
            "week, halting rail traffic."
        ),
        "icon": "bridge",
    },
    {
        "kicker": "ENERGY  •  THE GULF",
        "headline": "Tankers hit mines off Hormuz",
        "body": (
            "Three oil tankers catch fire after hitting mines east of the "
            "Strait of Hormuz."
        ),
        "icon": "tanker",
    },
    {
        "kicker": "SOUTH ASIA  •  BANGLADESH",
        "headline": "Unrest rocks Bangladesh",
        "body": (
            "Protests by Hasina's party shut parts of the country; interim "
            "leader Yunus's home is set ablaze."
        ),
        "icon": "flame",
    },
    {
        "kicker": "THE GULF  •  RIYADH",
        "headline": "Riyadh tower hit by Houthis",
        "body": (
            "A skyscraper housing Saudi Arabia's sovereign wealth fund HQ "
            "is damaged in an attack by Yemen's Houthis."
        ),
        "icon": "tower",
    },
    {
        "kicker": "CULTURE  •  GAMES",
        "headline": "Grand Theft Auto VI launches",
        "body": (
            "Grand Theft Auto VI launches to global fanfare, ending a "
            "13-year wait."
        ),
        "icon": "pad",
    },
]

ALSO_TODAY = (
    "ALSO TODAY: COP31 ministers try to unblock talks in Antalya  •  "
    "Voyager 1 reaches one light-day from Earth  •  Anthropic's record "
    "market debut"
)

FOOTER = "One day, one page  •  19 November 2026  •  make.fun"
