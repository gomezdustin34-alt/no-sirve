import subprocess, sys, re
O = "/tmp/claude-0/-home-user-no-sirve/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/scratchpad/out/"
OUT = sys.argv[1]
X = 0.6
import os
parts = [(O + "m1.mov", O + "m1.mov")] + [(O + f"m{i}.video.mp4", O + f"m{i}.audio.wav") for i in range(2, 9) if os.path.exists(O + f"m{i}.video.mp4")]
print([p[0].rsplit("/",1)[1] for p in parts])
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
def lufs(f):
    e = subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", e, re.M)[-1])
args = ["ffmpeg", "-v", "error", "-y"]; fc = []; vi = 0
for k, (v, a) in enumerate(parts):
    args += ["-i", v]; iv = vi; vi += 1
    if a != v: args += ["-i", a]; ia = vi; vi += 1
    else: ia = iv
    g = -16 - lufs(a); nf = -25 if k == 1 else -30
    fc.append(f"[{iv}:v]fps=30,format=yuv420p,setsar=1[v{k}]")
    fc.append(f"[{ia}:a]highpass=f=80,afftdn=nf={nf},volume={g:.2f}dB,aformat=sample_rates=48000:channel_layouts=mono[a{k}]")
durs = [dur(v) for v, _ in parts]
off = 0; pv = "v0"; pa = "a0"
for k in range(1, len(parts)):
    off += durs[k - 1] - X
    fc.append(f"[{pv}][v{k}]xfade=transition=fade:duration={X}:offset={off:.3f}[vx{k}]")
    fc.append(f"[{pa}][a{k}]acrossfade=d={X}:c1=tri:c2=tri[ax{k}]")
    pv, pa = f"vx{k}", f"ax{k}"
    off = off  # offset accumulates as start of next part
total = sum(durs) - X * (len(parts) - 1)
fc.append(f"[{pv}]fade=in:st=0:d=0.5,fade=out:st={total - 1:.3f}:d=1[v]")
fc.append(f"[{pa}]alimiter=limit=0.89,afade=out:st={total - 1:.3f}:d=1,aformat=channel_layouts=stereo[a]")
args += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("durs", durs, "total", total, dur(OUT))
