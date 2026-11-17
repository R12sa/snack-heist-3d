# Edit settings for the story "Me and my dad have a secret"
EXTRA = {'end': .9}
def config(L, S0):
    CARDS = {
     'bed': [("3:00 AM", "#ffd34d", .1, 9, 110, 140)],
     'parents': [("ZZZ...", "#cfe0ff", .2, 9, 100, 140)],
     'plead': [("MEOW!", "#ffb35c", L['plead'] - .9, 9, 150, 160)],
     'dadwake': [("*CLICK*", "#ffd34d", .55, 9, 100, 140)],
     'cake': [("MY BIRTHDAY CAKE?!", "#ff8ab8", 1.6, 9, 96, 140)],
     'turn': [("!!!", "#ff4b4b", 1.05, 9, 150, 140)],
     'deal': [("DEAL.", "#7dff8a", .05, 9, 130, 150)],
     'mom': [("MOM.", "#ff4b4b", 1.55, 9, 150, 150)],
     'end': [("WOULD YOU SNITCH?", "#ffd34d", .1, 9, 110, 150), ("SNACK HEIST - ON ROBLOX", "#ffffff", 1.4, 9, 64, 260)],
    }
    
    EMPH = {"secret.": "#ffd34d", "3": "#ffd34d", "starving.": "#ff8ab8", "cookie": "#ffd34d", "jar": "#ffd34d", "lawnmower.": "#7dff8a", "creaky": "#ff5050",
            "Whiskers.": "#ffb35c", "dare.": "#ff5050", "light": "#ffd34d", "sprint": "#ffd34d", "island.": "#7dff8a", "Flashlight": "#ffd34d", "everywhere.": "#ff5050",
            "birthday": "#ff8ab8", "cake.": "#ff8ab8", "eating": "#ff8ab8", "sees": "#ff5050", "stare": "#ffd34d", "anything.": "#7dff8a", "Deal.": "#7dff8a",
            "snacks": "#ffd34d", "Mom": "#ff5050", "snitch": "#ff5050"}
    
    SFX = [("Sting1", 0, .7), ("Tick1", S0('bed'), .5), ("Win1", S0('jar') + .4, .45), ("Creak1", S0('out') + .2, .7), ("Steps1", S0('hall'), .35),
           ("SnoreDad1", S0('parents'), .9), ("Steps1", S0('stairs'), .35), ("Creak3", S0('stairs') + 1.5, .25), ("Glimpse1", S0('cat'), .7),
           ("Heartbeat1", S0('catclose'), .6), ("Switch1", S0('dadwake') + .55, 1.0), ("WakeSting1", S0('dadwake') + .6, .7),
           ("Steps1", S0('grab'), .8), ("Glass1", S0('grab') + 1.75, .5), ("Heartbeat1", S0('hide'), .9), ("Steps1", S0('dadin'), .7), ("Heartbeat1", S0('dadin') + 1.2, .7),
           ("Steps1", S0('cake'), .6), ("Crunch1", S0('eat') + .4, 1.0), ("Crunch1", S0('eat') + 1.0, .9), ("Spotted1", S0('turn') + 1.05, .9),
           ("Tick1", S0('stare'), .6), ("Win1", S0('deal') + .1, .5), ("Crunch1", S0('split') + .5, .7), ("Crunch1", S0('split') + 1.4, .6),
           ("Switch1", S0('mom') + .3, .8), ("Jumpscare1", S0('mom') + 1.55, .8), ("Drone1", S0('end'), .7)]
    
    duck = f"if(between(t\\,{S0('hide')}\\,{S0('split')})\\,0.05\\,if(gt(t\\,{S0('mom')})\\,0.04\\,0.09))"
    
    return dict(cards=CARDS, emph=EMPH, sfx=SFX, duck=duck, meow=[S0('plead') + L['plead'] - .88],
                grade={'end': "colorbalance=rs=.12:gs=-.04:bs=-.06"})
