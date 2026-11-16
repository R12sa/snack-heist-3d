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
