# Fotorealistisk-ish fotboll: strålspårad sfär med trunkerad ikosaeder (12 svarta femhörningar, sömmar), ljus och skugga
import numpy as np, math
phi=(1+5**.5)/2
ico=np.array([[-1,phi,0],[1,phi,0],[-1,-phi,0],[1,-phi,0],[0,-1,phi],[0,1,phi],[0,-1,-phi],[0,1,-phi],[phi,0,-1],[phi,0,1],[-phi,0,-1],[-phi,0,1]],float)
ico/=np.linalg.norm(ico,axis=1)[:,None]
# hexagon-centra = dodekaederns hörn
dod=[]
for s in [(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]: dod.append(s)
for a in (-1,1):
    for b in (-1,1):
        dod+= [(0,a/phi,b*phi),(a/phi,b*phi,0),(a*phi,0,b/phi)]
dod=np.array(dod,float); dod/=np.linalg.norm(dod,axis=1)[:,None]
faces=np.vstack([ico,dod]); ispent=np.r_[np.ones(12,bool),np.zeros(20,bool)]
def rot(ax,ay):
    Rx=np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]]);Ry=np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]]);return Rx@Ry
def render_ball(r, ax=0.3, ay=0.0, light=(-0.5,-0.7,0.8)):
    S=int(r*2+4); yy,xx=np.mgrid[0:S,0:S].astype(float); cx=cy=S/2
    nx=(xx-cx)/r; ny=(yy-cy)/r; d2=nx**2+ny**2; m=d2<1
    nz=np.sqrt(np.clip(1-d2,0,1)); N=np.stack([nx,ny,nz],-1)
    R=rot(ax,ay); Nb=N@R.T
    dots=Nb.reshape(-1,3)@faces.T; idx=np.argsort(-dots,axis=1); top=np.take_along_axis(dots,idx[:,:2],1)
    pent=ispent[idx[:,0]]; seam=(top[:,0]-top[:,1])<0.012
    base=np.where(pent,28,238).astype(float); base=np.where(seam,np.where(pent,28,150),base).reshape(S,S)
    L=np.array(light);L/=np.linalg.norm(L)
    lam=np.clip((N@L),0,1); spec=np.clip(N@((L+np.array([0,0,1]))/np.linalg.norm(L+np.array([0,0,1]))),0,1)**30
    shade=0.28+0.78*lam
    col=base*shade+255*0.35*spec*(base>100)
    rgb=np.stack([col*1.0,col*0.99,col*0.97],-1)
    alpha=np.clip((1-np.sqrt(d2))*r*1.5,0,1)*m
    return np.clip(rgb,0,255), alpha
