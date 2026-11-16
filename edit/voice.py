import json, subprocess, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "voice")); k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
KID = 0.75 * k.get_voice_style("am_liam") + 0.25 * k.get_voice_style("am_michael")
DAD = 0.7 * k.get_voice_style("am_onyx") + 0.3 * k.get_voice_style("am_fenrir")
L = [("Me and my dad have a secret.", .95, .45, -1, KID, "hook"),
     ("So it's 3 AM. And I'm starving.", 1.0, .3, 0, KID, "bed"),
     ("Mom hid the cookie jar in the kitchen. Like I wouldn't find it.", 1.06, .35, 1, KID, "jar"),
     ("So I roll out of bed...", 1.0, .15, -1, KID, "out"),
     ("and sneak past my parents' room.", 1.0, .25, 0, KID, "hall"),
     ("Dad's snoring like a lawnmower.", 1.04, .4, 1, KID, "parents"),
     ("Down the stairs. Skip the creaky one.", 1.02, .4, 0, KID, "stairs"),
     ("And then... Whiskers.", .9, .2, -2, KID, "cat"),
     ("Just sitting there. Staring at me.", .95, .3, -1, KID, "catclose"),
     ("Whiskers. Don't you dare.", .9, 1.1, -2, KID, "plead"),
     ("Upstairs, Dad's light clicks on.", .98, .35, -2, KID, "dadwake"),
     ("So I sprint to the kitchen, grab the jar...", 1.1, .1, 2, KID, "grab"),
     ("and hide behind the island.", 1.05, .35, 1, KID, "hide"),
     ("Dad walks in. Flashlight on. Looking everywhere.", .98, .35, -1, KID, "dadin"),
     ("Then he walks right past me... to my birthday cake.", 1.0, .25, 0, KID, "cake"),
     ("And just starts eating it.", 1.0, .45, 2, KID, "eat"),
     ("Then he turns around. And sees me.", .95, .35, -2, KID, "turn"),
     ("We just stare at each other.", .95, .5, -1, KID, "stare"),
     ("You didn't see anything.", .9, .35, 0, DAD, "dadsays"),
     ("Deal.", .95, .5, 1, KID, "deal"),
     ("So now we split snacks every night.", 1.04, .3, 2, KID, "split"),
     ("Until last night... when Mom came downstairs.", .95, .5, -2, KID, "mom"),
     ("Be honest. Would you snitch on your dad?", 1.04, 1.2, 1, KID, "end")]
sr = 24000; out = []; meta = []; t = 0
for i, (txt, sp, gap, pc, voice, shot) in enumerate(L):
    sp *= 1.05; gap *= 0.9
    a, sr = k.create(txt, voice=voice, speed=sp, lang="en-us")
    nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0] - 240):nz[-1] + 600]
    sf.write("_l.wav", a, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "_l.wav", "-af", f"rubberband=pitch={1 + pc/100:.3f}:formant=preserved", "_p.wav"], check=True)
    a, _ = sf.read("_p.wav", dtype="float32")
    d = len(a) / sr; meta.append(dict(i=i, text=txt.replace("...", ""), start=round(t, 3), dur=round(d, 3), gap=gap, shot=shot, dad=voice is DAD)); out.append(a)
    out.append(np.zeros(int(gap * sr), dtype=np.float32)); t += d + gap
sf.write("story_raw.wav", np.concatenate(out), sr); json.dump(meta, open("story.json", "w"), indent=1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "story_raw.wav", "-af",
    "highpass=f=80,equalizer=f=220:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=1.5,equalizer=f=7500:t=q:w=1:g=-2,acompressor=threshold=-20dB:ratio=3:attack=8:release=120,aecho=0.85:0.5:28:0.10,aresample=48000",
    "story.wav"], check=True)
a, sr = k.create("Mrreeow!", voice=k.get_voice_style("af_sky"), speed=0.8, lang="en-us")
nz=np.where(np.abs(a)>0.01)[0]; a=a[nz[0]:nz[-1]+400]; sf.write("_m.wav", a, sr)
subprocess.run(["ffmpeg","-v","error","-y","-i","_m.wav","-af","rubberband=pitch=1.6:formant=shifted,highpass=f=300,aecho=0.8:0.6:40:0.2,volume=1.6,aresample=48000","meow.wav"],check=True)
print(round(t, 1))
