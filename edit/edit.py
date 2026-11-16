# Turns the rendered frames into the final video: captions, sound effects, voice, music.
#   python edit/edit.py [frames_dir] [output.mp4]
import json, os, re, subprocess, shutil, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
A = ROOT + "/assets/"
FR = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ROOT + "/frames") + "/"
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else ROOT + "/SnackHeist_Story.mp4")
W, H, FPS = 1920, 1080, 24
SFXD = A + "sfx/"; WH = A + "sfx/whoosh.wav"; MEOW = A + "voice/meow.wav"; MUS = A + "music.mp3"; FONT = A + "font.ttf"
WK = A + "voice/"
meta = json.load(open(WK + "story.json"))
EXTRA = {'end': .9}
st = {m['shot']: m for m in meta}
L = {m['shot']: m['dur'] + m['gap'] + EXTRA.get(m['shot'], 0) for m in meta}
END = meta[-1]['start'] + L['end']
def run(a): subprocess.run(a, check=True)
os.makedirs(ROOT + "/work", exist_ok=True); os.chdir(ROOT + "/work")
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
segs = []
for m in meta:
    n = m['shot']; N = int(round(L[n] * FPS)); have = len([f for f in os.listdir(FR + n) if f.endswith('.jpg')]) if os.path.isdir(FR + n) else 0
    if have < N: print('missing', n, have, N); sys.exit(1)
    vf = f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,setsar=1"
    vf += f",scale=w='{W}*(1+0.035*max(0\\,1-n/5))':h='{H}*(1+0.035*max(0\\,1-n/5))':eval=frame,crop={W}:{H}"
    if n == 'end': vf += ",colorbalance=rs=.12:gs=-.04:bs=-.06"
    for k, (txt, col, a, b, sz, y) in enumerate(CARDS.get(n, [])):
        fn = f"c_{n}{k}.txt"; open(fn, "w").write(txt)
        vf += (f",drawtext=fontfile={FONT}:textfile={fn}:fontcolor={col}:borderw={max(8, sz//11)}:bordercolor=black:shadowcolor=black@0.55:shadowy={sz//14}:"
               f"fontsize='{sz}*(1+0.28*max(0\\,1-(t-{a:.3f})/0.1))':x=(w-text_w)/2:y={y}-text_h/2:enable='between(t\\,{a:.3f}\\,{b:.3f})'")
    if n == 'end': vf += f",fade=t=out:st={L[n]-.5:.3f}:d=0.5"
    run(["ffmpeg", "-v", "warning", "-y", "-framerate", str(FPS), "-start_number", "1", "-i", FR + n + "/f_%04d.jpg", "-vf", vf, "-frames:v", str(N),
         "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), f"s_{n}.tmp.mp4"])
    os.replace(f"s_{n}.tmp.mp4", f"s_{n}.mp4"); segs.append(f"s_{n}.mp4")
open("l.txt", "w").write("".join(f"file '{x}'\n" for x in segs))
run(["ffmpeg", "-v", "warning", "-y", "-f", "concat", "-safe", "0", "-i", "l.txt", "-c", "copy", "j.mp4"])
EMPH = {"secret.": "#ffd34d", "3": "#ffd34d", "starving.": "#ff8ab8", "cookie": "#ffd34d", "jar": "#ffd34d", "lawnmower.": "#7dff8a", "creaky": "#ff5050",
        "Whiskers.": "#ffb35c", "dare.": "#ff5050", "light": "#ffd34d", "sprint": "#ffd34d", "island.": "#7dff8a", "Flashlight": "#ffd34d", "everywhere.": "#ff5050",
        "birthday": "#ff8ab8", "cake.": "#ff8ab8", "eating": "#ff8ab8", "sees": "#ff5050", "stare": "#ffd34d", "anything.": "#7dff8a", "Deal.": "#7dff8a",
        "snacks": "#ffd34d", "Mom": "#ff5050", "snitch": "#ff5050"}
words = []
for m in meta:
    ws = m["text"].split(); wt = [len(re.sub(r"\W", "", w)) + 2 + (3 if w[-1] in ".,!?" else 0) for w in ws]
    tot = sum(wt); t = m["start"]
    for w, x in zip(ws, wt):
        d = m["dur"] * x / tot; words.append([w, t, t + d, m['dad']]); t += d
for i in range(len(words) - 1):
    if words[i + 1][1] - words[i][2] < .6: words[i][2] = words[i + 1][1]
words[-1][2] = END - .3
fl = []
for i, (w, a, b, dad) in enumerate(words):
    open(f"w{i}.txt", "w").write(re.sub(r"[,]$", "", w).upper())
    col = "#7dff8a" if dad else EMPH.get(w, "white"); sz = 112 if (w in EMPH or dad) else 96
    fl.append(f"drawtext=fontfile={FONT}:textfile=w{i}.txt:fontcolor={col}:borderw=10:bordercolor=black:shadowcolor=black@0.6:shadowy=8:"
              f"fontsize='{sz}*(1+0.28*max(0\\,1-(t-{a:.3f})/0.08))':x=(w-text_w)/2:y=915-text_h/2:enable='between(t\\,{a:.3f}\\,{b:.3f})'")
fl.append(f"drawbox=x=0:y=ih-10:w='iw*t/{END:.2f}':h=10:color=0xffd34d:t=fill")
open("vf.txt", "w").write(",".join(fl))
S0 = lambda n: st[n]['start']
SFX = [("Sting1", 0, .7), ("Tick1", S0('bed'), .5), ("Win1", S0('jar') + .4, .45), ("Creak1", S0('out') + .2, .7), ("Steps1", S0('hall'), .35),
       ("SnoreDad1", S0('parents'), .9), ("Steps1", S0('stairs'), .35), ("Creak3", S0('stairs') + 1.5, .25), ("Glimpse1", S0('cat'), .7),
       ("Heartbeat1", S0('catclose'), .6), ("Switch1", S0('dadwake') + .55, 1.0), ("WakeSting1", S0('dadwake') + .6, .7),
       ("Steps1", S0('grab'), .8), ("Glass1", S0('grab') + 1.75, .5), ("Heartbeat1", S0('hide'), .9), ("Steps1", S0('dadin'), .7), ("Heartbeat1", S0('dadin') + 1.2, .7),
       ("Steps1", S0('cake'), .6), ("Crunch1", S0('eat') + .4, 1.0), ("Crunch1", S0('eat') + 1.0, .9), ("Spotted1", S0('turn') + 1.05, .9),
       ("Tick1", S0('stare'), .6), ("Win1", S0('deal') + .1, .5), ("Crunch1", S0('split') + .5, .7), ("Crunch1", S0('split') + 1.4, .6),
       ("Switch1", S0('mom') + .3, .8), ("Jumpscare1", S0('mom') + 1.55, .8), ("Drone1", S0('end'), .7)]
ins = ["-i", WK + "story.wav", "-ss", "4", "-i", MUS]
duck = f"if(between(t\\,{S0('hide')}\\,{S0('split')})\\,0.05\\,if(gt(t\\,{S0('mom')})\\,0.04\\,0.09))"
fc = (f"[0]apad,atrim=0:{END},volume=1.7[vo];[1]atrim=0:{END},volume='{duck}':eval=frame,afade=t=in:d=0.5,afade=t=out:st={END-1.5}:d=1.5[m];")
labs = "[vo][m]"; n = 2
for nm, at, vol in SFX:
    f = SFXD + "SH_" + nm + ".ogg"
    if not os.path.exists(f): print('no sfx', nm); continue
    ms = int(max(0, at) * 1000); ins += ["-i", f]; fc += f"[{n}]aresample=48000,aformat=channel_layouts=stereo,atrim=0:3,adelay={ms}|{ms},volume={vol*.5}[a{n}];"; labs += f"[a{n}]"; n += 1
ms = int((S0('plead') + L['plead'] - .88) * 1000); ins += ["-i", MEOW]; fc += f"[{n}]aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=.9[a{n}];"; labs += f"[a{n}]"; n += 1
for m in meta[1:]:
    ms = int(max(0, m['start'] - .05) * 1000); ins += ["-i", WH]; fc += f"[{n}]adelay={ms}|{ms},volume=.12[a{n}];"; labs += f"[a{n}]"; n += 1
fc += f"{labs}amix=inputs={n}:normalize=0,atrim=0:{END},loudnorm=I=-14:TP=-1.5[a]"
open("af.txt", "w").write(fc)
run(["ffmpeg", "-v", "warning", "-y", *ins, "-filter_complex_script", "af.txt", "-map", "[a]", "-c:a", "pcm_s16le", "a.wav"])
run(["ffmpeg", "-v", "warning", "-y", "-i", "j.mp4", "-i", "a.wav", "-filter_script:v", "vf.txt", "-map", "0:v", "-map", "1:a",
     "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "t.mp4"])
shutil.move("t.mp4", OUT)
run(["ffmpeg", "-v", "warning", "-y", "-i", OUT, "-vf", "fps=1,scale=320:-2,tile=8x7", "-frames:v", "1", "chk.jpg"])
print(round(END, 1), len(segs), len(words))
