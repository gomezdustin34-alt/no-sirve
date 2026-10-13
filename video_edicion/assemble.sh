#!/bin/bash
set -e
O=/tmp/claude-0/-home-user-no-sirve/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/scratchpad/out
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
lufs() { ffmpeg -i "$1" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}'; }
D1=$(dur $O/m1.mov); D2=$(dur $O/m2.video.mp4)
G1=$(python3 -c "print(-16-($(lufs $O/m1.mov)))"); G2=$(python3 -c "print(-16-($(lufs $O/m2.audio.wav)))"); G3=$(python3 -c "print(-16-($(lufs $O/m3.audio.wav)))")
X=0.6
OF1=$(python3 -c "print($D1-$X)"); OF2=$(python3 -c "print($D1+$D2-2*$X)")
echo "gains $G1 $G2 $G3 offsets $OF1 $OF2"
ffmpeg -v error -y -i $O/m1.mov -i $O/m2.video.mp4 -i $O/m2.audio.wav -i $O/m3.video.mp4 -i $O/m3.audio.wav -filter_complex "
[0:v]fps=30,format=yuv420p,setsar=1[v1];[1:v]fps=30,format=yuv420p,setsar=1[v2];[3:v]fps=30,format=yuv420p,setsar=1[v3];
[v1][v2]xfade=transition=fade:duration=$X:offset=$OF1[v12];[v12][v3]xfade=transition=fade:duration=$X:offset=$OF2,fade=in:st=0:d=0.5[v];
[0:a]highpass=f=80,afftdn=nf=-30,volume=${G1}dB,aformat=sample_rates=48000:channel_layouts=mono[a1];
[2:a]highpass=f=80,afftdn=nf=-25,volume=${G2}dB,aformat=sample_rates=48000:channel_layouts=mono[a2];
[4:a]highpass=f=80,afftdn=nf=-30,volume=${G3}dB,aformat=sample_rates=48000:channel_layouts=mono[a3];
[a1][a2]acrossfade=d=$X:c1=tri:c2=tri[a12];[a12][a3]acrossfade=d=$X:c1=tri:c2=tri,alimiter=limit=0.89,aformat=channel_layouts=stereo[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 20 -profile:v high -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$1"
dur "$1"
