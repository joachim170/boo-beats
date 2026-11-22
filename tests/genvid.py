import numpy as np, math, subprocess
from PIL import Image, ImageDraw, ImageFilter
W,H=640,480; fps=15; secs=24
rng=np.random.default_rng(1)
# background: wall top 35%, floor below with perspective-ish noise
bg=np.zeros((H,W,3),np.float32)
bg[:int(H*.35)]=[200,198,192]
floor=np.linspace(150,120,H-int(H*.35))[:,None,None]*np.ones((1,W,1))
bg[int(H*.35):]=floor*np.array([1,0.97,0.92])
bg+=rng.normal(0,6,(H,W,3)); bg=np.clip(bg,0,255).astype(np.uint8)
base=Image.fromarray(bg)
d=ImageDraw.Draw(base); d.rectangle([380,40,560,150],fill=(235,240,245))  # window
def ball(r,rot):
    S=r*2+8; im=Image.new('RGBA',(S*4,S*4),(0,0,0,0)); dr=ImageDraw.Draw(im); c=S*2; R=r*4
    dr.ellipse([c-R,c-R,c+R,c+R],fill=(245,245,245,255))
    # pentagons
    pts=[(0,0)]+[(0.62*math.cos(a+rot),0.62*math.sin(a+rot)) for a in np.linspace(0,2*math.pi,6)[:-1]]
    for (px,py) in pts:
        rr=R*0.28*(1-0.5*math.hypot(px,py))
        poly=[(c+px*R+rr*math.cos(a+rot),c+py*R+rr*math.sin(a+rot)) for a in np.linspace(0,2*math.pi,6)[:-1]]
        dr.polygon(poly,fill=(25,25,25,255))
    # shading
    sh=Image.new('L',im.size,0); ds=ImageDraw.Draw(sh)
    for k in range(20): ds.ellipse([c-R+k*R/30+R*0.25,c-R+k*R/30+R*0.25,c+R,c+R],outline=int(k*4))
    im=im.resize((S,S),Image.LANCZOS); return im
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-pix_fmt','yuv420p','/tmp/claude-0/vid/ball.y4m'],stdin=subprocess.PIPE)
truth=[]
for f in range(fps*secs):
    t=f/fps
    # phases: 0-12s near (r=34, y~380), 12-24s far (r=14, y~260)
    near=t<12
    r=34 if near else 14; y=380 if near else 262
    # x moves between thirds: hold 1.2s, move 0.5s
    seq=[1,0,1,2,1,0,2,0,1,2,1,0,1,2]
    seg=t/1.7; i=int(seg)%len(seq); j=(i+1)%len(seq); fr=seg-int(seg)
    xs=[W*0.2,W*0.5,W*0.8]; a=xs[seq[i]]; b=xs[seq[j]]
    m=0 if fr<0.7 else (fr-0.7)/0.3; x=a+(b-a)*(m*m*(3-2*m))
    im=base.copy(); dr=ImageDraw.Draw(im,'RGBA'); dr.ellipse([x-r,y+r*0.7,x+r,y+r*1.1],fill=(0,0,0,60))
    bl=ball(r,t*3); im.paste(bl,(int(x-bl.width/2),int(y-bl.height/2)),bl)
    p.stdin.write(np.asarray(im.convert('RGB')).tobytes())
    truth.append((round(t,2),1-x/W))  # mirrored x as game sees it
p.stdin.close(); p.wait()
import json; json.dump(truth,open('/tmp/claude-0/vid/truth.json','w'))
im.save('/tmp/claude-0/vid/last.png')
print('ok')
