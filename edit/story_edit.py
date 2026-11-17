# Edit settings for the current story: Snack Heist gameplay showcase (Nights 1-3)
EXTRA = {'end': .8}
def config(L, S0):
    Y = 140
    def done(t): return ("NIGHT %s COMPLETE" % t, "#7dff8a")
    CARDS = {
        'hook': [("GET BACK TO BED!", "#ffffff", .05, 9, 96, Y), ("0:10", "#ff4b4b", .05, 9, 130, 270)],
        'title': [("SNACK HEIST", "#ffd34d", .1, 9, 180, 430), ("ON ROBLOX", "#ffffff", .45, 9, 72, 560)],
        'n1parents': [("NIGHT 1", "#cfe0ff", .05, 9, 130, Y)],
        'n1jar': [(*done(1), 1.3, 9, 100, Y)],
        'n2cat': [("NIGHT 2", "#ffb35c", .05, 9, 130, Y)],
        'n2dad': [("MEOW!", "#ffb35c", .0, .7, 140, Y)],
        'n2pass': [(*done(2), 1.2, 9, 100, Y)],
        'n3patrol': [("NIGHT 3", "#ff4b4b", .05, 9, 130, Y)],
        'n3stairs': [("0:05", "#ff4b4b", .0, 9, 150, Y)],
        'n3bed': [(*done(3), .25, 9, 110, Y), ("+ COINS", "#ffd34d", .5, 9, 80, 260)],
        'perks': [("NINJA", "#7dd3ff", .0, .55, 130, Y), ("SPEEDY", "#ffd34d", .55, 1.1, 130, Y), ("HIDER", "#7dff8a", 1.1, 1.65, 130, Y), ("PRANKSTER", "#ff8ab8", 1.65, 9, 130, Y)],
        'friends': [("SOLO TO 4-PLAYER PARTY", "#ffffff", .1, 9, 90, Y)],
        'cta': [("PLAY SNACK HEIST", "#ffd34d", .05, 9, 150, 420), ("ON ROBLOX", "#ffffff", .3, 9, 80, 545)],
        'end': [("CAN YOU BEAT NIGHT 3?", "#ffd34d", .1, 9, 104, Y)],
    }
    EMPH = {"ten": "#ff5050", "bed.": "#ffd34d", "Snack": "#ffd34d", "Heist.": "#ffd34d", "creak.": "#ff5050", "Easy.": "#7dff8a", "Whiskers": "#ffb35c",
            "meow,": "#ffb35c", "hide.": "#ffd34d", "couch.": "#ffd34d", "past": "#ff5050", "three.": "#ff5050", "Flashlights": "#ffd34d", "toy,": "#ffd34d",
            "cake.": "#ff8ab8", "run.": "#ff5050", "Five.": "#ff5050", "Made": "#7dff8a", "it.": "#7dff8a", "Ninja": "#7dd3ff", "Speedy.": "#ffd34d",
            "pajamas,": "#ff8ab8", "friends.": "#7dff8a", "Roblox.": "#ffd34d", "knocked": "#cfe0ff"}
    SFX = [("Heartbeat1", 0, 1.0), ("Steps1", 0, .8), ("Sting1", S0('title'), .8), ("Creak1", S0('loopbed') + .2, .6), ("Glass1", S0('loopsnack') + .8, .5),
           ("SnoreDad1", S0('n1parents'), .9), ("Steps1", S0('n1hall'), .35), ("Win1", S0('n1jar') + 1.3, .7),
           ("Glimpse1", S0('n2cat'), .8), ("Switch1", S0('n2dad') + .5, 1.0), ("WakeSting1", S0('n2dad') + .55, .7), ("Heartbeat1", S0('n2hide'), .9),
           ("Steps1", S0('n2pass'), .8), ("Win1", S0('n2pass') + 1.2, .7), ("Drone1", S0('n3patrol'), .7), ("Steps1", S0('n3patrol') + .4, .6),
           ("Throw1", S0('n3throw') + .35, 1.0), ("Land1", S0('n3throw') + 1.1, .9), ("Steps1", S0('n3cake'), .9), ("Heartbeat1", S0('n3stairs'), 1.0),
           ("Steps1", S0('n3stairs'), 1.0), ("DoorOpen1", S0('n3bed') + .2, .9), ("Win1", S0('n3bed') + .3, .9), ("Click1", S0('perks'), .6),
           ("Click1", S0('perks') + .55, .6), ("Click1", S0('perks') + 1.1, .6), ("Click1", S0('perks') + 1.65, .6), ("Win1", S0('cta'), .6), ("Creak2", S0('end') + .3, .5)]
    duck = f"if(between(t\\,{S0('n2hide')}\\,{S0('perks')})\\,0.06\\,0.11)"
    return dict(cards=CARDS, emph=EMPH, sfx=SFX, duck=duck, meow=[S0('n2dad') + .02], music_start=20,
                grade={'title': "eq=saturation=1.1:contrast=1.05", 'hook': "eq=contrast=1.1:saturation=1.15"})
