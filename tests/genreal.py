import numpy as np, math, subprocess, json, sys
sys.path.insert(0,'/tmp/claude-0'); from realball import render_ball
from PIL import Image, ImageDraw, ImageFilter
W,H=640,480; fps=15
rng=np.random.default_rng(2)
# bakgrund: vägg + golv (laminat-känsla) med perspektivränder
bg=np.zeros((H,W,3),np.float32); hz=int(H*.33)
bg[:hz]=[205,200,190]; yy=np.arange(H-hz)[:,None]; xx=np.arange(W)[None,:]
plank=((xx-W/2)*(0.4+yy/(H-hz))/38).astype(int)%2
bg[hz:]=(np.array([150,125,95])*(0.85+0.1*plank[...,None])*(0.8+0.3*yy[...,None]/(H-hz)))
bg+=rng.normal(0,5,(H,W,3)); base=np.clip(bg,0,255)
def frame(bx,by,r,t,foot=None,cover=False):
    k=r/30
    im=base.copy()
    # skugga
    yy,xx=np.mgrid[0:H,0:W]; sh=np.exp(-(((xx-bx-r*.2)/(r*1.1))**2+((yy-by-r*.9)/(r*.35))**2)); im*= (1-0.45*sh)[...,None]
    rgb,a=render_ball(r,ax=t*2.1,ay=t*3.3); S=rgb.shape[0]; x0=int(bx-S/2); y0=int(by-S/2)
    sub=im[y0:y0+S,x0:x0+S]; aa=a[:sub.shape[0],:sub.shape[1],None]; sub[:]=sub*(1-aa)+rgb[:sub.shape[0],:sub.shape[1]]*aa
    pil=Image.fromarray(im.astype(np.uint8))
    if foot:
        fx,fy=foot; d=ImageDraw.Draw(pil); d.rounded_rectangle([fx-16*k,fy-150*k,fx+16*k,fy-22*k],max(2,int(8*k)),fill=(60,70,120)); d.ellipse([fx-46*k,fy-34*k,fx+34*k,fy+12*k],fill=(25,25,32))
    return pil.filter(ImageFilter.GaussianBlur(0.6))
if __name__=='__main__':
    out=sys.argv[1]; withfoot=len(sys.argv)>2
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    truth=[]
    for f in range(fps*24):
        t=f/fps; near=t<12; r=30 if near else 13; by=390 if near else 245
        xs=[W*.2,W*.5,W*.8]; seq=[1,0,1,2,1,0,2,0,1,2,1,0]
        seg=t/1.7; i=int(seg)%len(seq); j=(i+1)%len(seq); fr=seg-int(seg); m=0 if fr<.65 else (fr-.65)/.35; m=m*m*(3-2*m)
        bx=xs[seq[i]]+(xs[seq[j]]-xs[seq[i]])*m
        foot=None
        if withfoot:
            cover=(t%4)>3.1 and (t%4)<3.7; foot=(bx if cover else bx+r*2.6*math.sin(t*2.3), by-(0 if cover else r*.8))
        im=frame(bx,by,r,t,foot); p.stdin.write(np.asarray(im).tobytes()); truth.append([round(t,3),1-bx/W,by/H,r])
        if f in (30,250): im.save(out.replace('.y4m',f'_{f}.png'))
    p.stdin.close(); p.wait(); json.dump(truth,open(out.replace('.y4m','.json'),'w')); print('ok')
