# Render frames. Splits the whole video into N equal chunks so many computers can render at once.
#   python render.py --chunk 3 --of 20 --out frames      (one chunk)
#   python render.py --out frames                          (everything, on one computer)
import bpy, sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import *
import shots
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--chunk', type=int, default=0); ap.add_argument('--of', type=int, default=1)
ap.add_argument('--out', default=os.path.join(ROOT, 'frames')); ap.add_argument('--spp', type=int, default=8)
ap.add_argument('--width', type=int, default=960); ap.add_argument('--height', type=int, default=540)
ap.add_argument('--shots', default='all')
a = ap.parse_args(argv)
meta = json.load(open(os.path.join(ROOT, 'assets', 'voice', 'story.json')))
EXTRA = {'end': .9}
jobs = []   # every frame in the video: (shot, frame, length)
for m in meta:
    n = m['shot']
    if a.shots != 'all' and n not in a.shots.split(','): continue
    L = m['dur'] + m['gap'] + EXTRA.get(n, 0)
    jobs += [(n, f, L) for f in range(1, int(round(L * FPS)) + 1)]
per = -(-len(jobs) // a.of); mine = jobs[a.chunk * per:(a.chunk + 1) * per]
print(f'chunk {a.chunk}/{a.of}: {len(mine)} of {len(jobs)} frames', flush=True)
G = build(res=(a.width, a.height), spp=a.spp); S = G['S']; cur = {}
def handler(scene, *x):
    shots.reset(G); shots.SHOTS[cur['n']]((scene.frame_current - 1) / FPS, G, cur['L'])
bpy.app.handlers.frame_change_pre.append(handler)
S.render.use_overwrite = False
i = 0; t0 = time.time()
while i < len(mine):  # render each run of frames from the same shot as one animation
    n, f, L = mine[i]; j = i
    while j + 1 < len(mine) and mine[j + 1][0] == n and mine[j + 1][1] == mine[j][1] + 1: j += 1
    os.makedirs(os.path.join(a.out, n), exist_ok=True)
    cur['n'] = n; cur['L'] = L
    S.frame_start, S.frame_end = f, mine[j][1]; S.render.filepath = os.path.join(a.out, n, 'f_')
    bpy.ops.render.render(animation=True)
    print('done', n, f, mine[j][1], round(time.time() - t0), 's', flush=True)
    i = j + 1
