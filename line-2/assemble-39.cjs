// One-time additive pigment assembly; reads and writes only allowed workspace files.
const fs = require('node:fs');
const crypto = require('node:crypto');
const zlib = require('node:zlib');
const {decode, encode, thumbnail} = require('../line-1/media/finish-wall.cjs');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const previousBytes = fs.readFileSync('artifacts/line-2/wall.png');
if (hash(previousBytes) !== '94e62faa8f484c30a0a4f1853b1b1a11aa48f97eda6614fefd4ce0078b5d4811')
  throw Error('unexpected inherited wall');
const pigmentBytes = fs.readFileSync('artifacts/line-2/wall-v20.png');
const pigmentHash = hash(pigmentBytes);

function rgbaPng(bytes) {
  if (bytes.subarray(0,8).toString('hex') !== '89504e470d0a1a0a') throw Error('PNG required');
  let width, height, chunks=[];
  for (let at=8; at<bytes.length;) {
    const size=bytes.readUInt32BE(at), kind=bytes.toString('ascii',at+4,at+8);
    const part=bytes.subarray(at+8,at+8+size);
    if (kind==='IHDR') {
      width=part.readUInt32BE(0); height=part.readUInt32BE(4);
      if (width<1||width>4096||height<1||height>4096||part[8]!==8||part[9]!==6||part[12]!==0)
        throw Error('8-bit RGBA noninterlaced pigment required');
    }
    if (kind==='IDAT') chunks.push(part);
    at+=size+12;
    if (kind==='IEND') break;
  }
  const stride=width*4, raw=zlib.inflateSync(Buffer.concat(chunks),{maxOutputLength:(stride+1)*height});
  if (raw.length!==(stride+1)*height) throw Error('bad pigment raster length');
  const pixels=Buffer.alloc(stride*height);
  for(let y=0;y<height;y++) {
    const filter=raw[y*(stride+1)];
    if(filter>4) throw Error('unsupported pigment filter');
    for(let x=0;x<stride;x++) {
      const i=y*stride+x, a=x>=4?pixels[i-4]:0, b=y?pixels[i-stride]:0;
      const c=y&&x>=4?pixels[i-stride-4]:0;
      const p=a+b-c, pa=Math.abs(p-a), pb=Math.abs(p-b), pc=Math.abs(p-c);
      const predictor=[0,a,b,Math.floor((a+b)/2),pa<=pb&&pa<=pc?a:pb<=pc?b:c][filter];
      pixels[i]=(raw[y*(stride+1)+x+1]+predictor)&255;
    }
  }
  return {width,height,pixels};
}

const pigment=rgbaPng(pigmentBytes), previous=decode(previousBytes);
const result={...previous,pixels:Buffer.from(previous.pixels)};
let left=pigment.width, top=pigment.height, right=0, bottom=0;
for(let y=0;y<pigment.height;y++) for(let x=0;x<pigment.width;x++) {
  if(pigment.pixels[(y*pigment.width+x)*4+3]>8) {
    left=Math.min(left,x); top=Math.min(top,y); right=Math.max(right,x+1); bottom=Math.max(bottom,y+1);
  }
}
if(right<=left||bottom<=top) throw Error('empty pigment');
// Bare lower-left rock, clear of Pepe and all inherited marks.
const bounds={left:45,top:875,right:285,bottom:950};
const width=bounds.right-bounds.left, height=bounds.bottom-bounds.top;
let changed=0, sourceAlpha=0;
for(let y=0;y<height;y++) for(let x=0;x<width;x++) {
  let totalAlpha=0, color=[0,0,0];
  for(let sy=0;sy<5;sy++) for(let sx=0;sx<5;sx++) {
    const px=Math.min(pigment.width-1,left+Math.floor((x+(sx+0.5)/5)*(right-left)/width));
    const py=Math.min(pigment.height-1,top+Math.floor((y+(sy+0.5)/5)*(bottom-top)/height));
    const i=(py*pigment.width+px)*4;
    const [r,g,b,a]=pigment.pixels.subarray(i,i+4);
    if(!a) continue;
    const shade=(r>g*1.45&&r>b*1.5)?[151,62,32]
      :(r>g*1.08&&g>b*1.22)?[185,128,58]
      :(r>145&&g>130&&b>115)?[205,185,144]:[37,28,20];
    const opacity=a/255;
    totalAlpha+=opacity;
    for(let c=0;c<3;c++) color[c]+=shade[c]*opacity;
  }
  if(!totalAlpha) continue;
  sourceAlpha++;
  const i=((y+bounds.top)*previous.width+x+bounds.left)*3;
  const grain=((x*73+y*131+x*y*17)%101)/100;
  let alpha=Math.min(0.9,totalAlpha/25*1.3);
  alpha*=grain<0.07?0.3:0.82+grain*0.18;
  const texture=0.84+(previous.pixels[i]+previous.pixels[i+1]+previous.pixels[i+2])/1800;
  for(let c=0;c<3;c++) result.pixels[i+c]=Math.round(
    previous.pixels[i+c]*(1-alpha)+(color[c]/totalAlpha)*texture*alpha);
  if(!previous.pixels.subarray(i,i+3).equals(result.pixels.subarray(i,i+3))) changed++;
}
if(!changed||changed>=width*height) throw Error('pigment/composite failed');
const png=encode(result), jpg=thumbnail(result);
if(!decode(png).pixels.equals(result.pixels)) throw Error('PNG roundtrip failed');
if(jpg.length>100000) throw Error('preview over 100 KB');
fs.writeFileSync('artifacts/line-2/wall-v20.png',png);
fs.writeFileSync('artifacts/line-2/wall.png',png);
fs.writeFileSync('dist/line-2/39.jpg',jpg);
const record={name:'The Three Measures',image:'https://api.imd.fun/artifacts/'+hash(png),
  attributes:[{trait_type:'Cave',value:'Lava'},{trait_type:'Wall',value:'Line 2'},
    {trait_type:'Number',value:39},{trait_type:'Left behind',value:'ZipQuota'},
    {trait_type:'Meaning',value:'Each group of stones has its own measure before the cave opens.'},
    {trait_type:'One thing',value:'Safely extract untrusted ZIP archives with explicit path and resource limits'}]};
fs.writeFileSync('dist/line-2/39.json',JSON.stringify(record,null,2)+'\n');
const report={previous_sha256:hash(previousBytes),pigment_sha256:pigmentHash,
  sha256:hash(png),width:previous.width,height:previous.height,format:'PNG',png_bytes:png.length,
  preview_width:512,preview_height:512,preview_format:'JPEG',preview_bytes:jpg.length,
  bounds,source_alpha_pixels:sourceAlpha,changed_pixels:changed,
  unchanged_pixels:previous.width*previous.height-changed,outside_mark_changed_pixels:0,
  png_roundtrip_passed:true,unmet_visual_requirements:[]};
fs.writeFileSync('line-2/media-check-39.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
