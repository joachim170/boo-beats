# Video: boll + en fot (svart sko med grå strumpa) som rör sig nära och ibland täcker bollen
import numpy as np, math, subprocess, json
from PIL import Image, ImageDraw
exec(open('/tmp/claude-0/genvid.py').read().split("p=subprocess.Popen")[0])  # återanvänd bakgrund + ball()
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-pix_fmt','yuv420p','/tmp/claude-0/vid/foot.y4m'],stdin=subprocess.PIPE)
truth=[]
for f in range(fps*20):
    t=f/fps; r=30; y=380
    xs=[W*0.2,W*0.5,W*0.8]; seq=[1,0,1,2,1,0,2,1]
    seg=t/2.0; i=int(seg)%len(seq); j=(i+1)%len(seq); fr=seg-int(seg); m=0 if fr<0.6 else (fr-0.6)/0.4; m=m*m*(3-2*m)
    bx=xs[seq[i]]+(xs[seq[j]]-xs[seq[i]])*m
    # foten följer bollen på sidan, och var 4:e sekund kliver den över bollen i 0.6 s
    cover=(t%4)>3.2 and (t%4)<3.8
    fx=bx+(0 if cover else 70*math.sin(t*2.3)); fy=y-(0 if cover else 25)
    im=base.copy(); dr=ImageDraw.Draw(im,'RGBA')
    dr.ellipse([bx-r,y+r*0.7,bx+r,y+r*1.1],fill=(0,0,0,60))
    bl=ball(r,t*3); im.paste(bl,(int(bx-bl.width/2),int(y-bl.height/2)),bl)
    dr.rectangle([fx-14,fy-140,fx+14,fy-20],fill=(150,150,155,255))   # strumpa/ben
    dr.ellipse([fx-40,fy-30,fx+30,fy+12],fill=(20,22,30,255))         # sko
    p.stdin.write(np.asarray(im.convert('RGB')).tobytes())
    truth.append([round(t,2),1-bx/W,cover])
p.stdin.close(); p.wait(); json.dump(truth,open('/tmp/claude-0/vid/foot.json','w')); im.save('/tmp/claude-0/vid/foot.png'); print('ok')
