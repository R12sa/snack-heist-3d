# Snack Heist 3D Story Maker

Makes the Snack Heist 3D story video ("Me and my dad have a secret") in Blender, inside the real Snack Heist house.

**Fast way: GitHub does the work.** Instead of one slow computer, 20 GitHub computers each render a piece at the same time, then one puts it all together.

## Make the video
1. Go to the **Actions** tab, then **Render Snack Heist story**, then **Run workflow**.
2. Wait about 15–20 minutes.
3. Open the finished run and download **SnackHeist_Story** at the bottom.

Pick `fast` for a quick low-quality test.

## What's inside
- `assets/house.gltf`: your house, exported from Roblox Studio (Save / Export, then Export as glTF)
- `render/shots.py`: every shot (who moves where, the camera, faces)
- `render/lib.py`: characters, cat, props, helpers
- `edit/edit.py`: captions, sound effects, voice, music
- `edit/voice.py`: makes the voiceover (needs the Kokoro model files)

## Run on one computer
```
pip install bpy==5.3.0
python render/render.py -- --out frames
python edit/edit.py frames SnackHeist_Story.mp4
```

## New towns (town maker)
Stories can happen in your Snack Heist house **or** in a brand-new town built in under a second.

Make `assets/place.json`:
```
{"place": "town", "seed": 7, "theme": "suburb", "time": "day", "size": 3}
```
- `seed`: any number. A new number gives a new town, and the same number gives the same town.
- `theme`: `suburb`, `city`, `beach`, `snow`
- `time`: `day`, `sunset`, `night`
- `size`: blocks per side (3 = 9 blocks)

No `place.json` (or `"place": "house"`) = your Snack Heist house.

Every town has houses with doors facing the road, sidewalks, trees, streetlights, mailboxes, plus a school, gas station and shop. When a render runs, `assets/town_layout.json` is written with every door, road and intersection spot so shots know where to go.

Quick look at a town: `python render/town_preview.py -- 7 suburb day town.jpg`
