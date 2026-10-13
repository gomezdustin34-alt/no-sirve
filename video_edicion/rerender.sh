cd /tmp/claude-0/-home-user-no-sirve/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/scratchpad
(python3 -I m3/render.py out/m3 > out/m3.log 2>&1; python3 -I m3/render_m5.py out/m5 > out/m5.log 2>&1; python3 -I m3/render_m6.py out/m6 > out/m6.log 2>&1) &
(python3 -I m3/render_m2.py out/m2 > out/m2.log 2>&1; python3 -I m3/render_m4.py out/m4 > out/m4.log 2>&1; python3 -I m3/render_m8.py out/m8 > out/m8.log 2>&1) &
wait
python3 m3/assemble.py /home/user/no-sirve/video_edicion/Taller_Funciones_Video_Final.mp4 > out/assemble.log 2>&1
echo ALLDONE
