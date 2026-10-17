// One-shot local assembly from imagegen's base64 pigment; no image intermediate saved.
const fs=require('node:fs'), zlib=require('node:zlib'), crypto=require('node:crypto');
const media=require('./png_codec.cjs');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const source='artifacts/line-3/wall-v19.png', target='artifacts/line-3/wall-v20.png';
const pigmentPath='artifacts/line-3/pigment-base64.txt';
const oldBytes=fs.readFileSync(source), pigment=Buffer.from(fs.readFileSync(pigmentPath,'utf8').trim(),'base64');
if(hash(oldBytes)!=='c3c41e2fc90372b0038bd5962b901b9bcb4de15a9623d55431ecf98149c3f252') throw Error('Wrong ancestor');
function rgba(bytes) {
  if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a') throw Error('PNG required');
  let w,h,parts=[];
  for(let pos=8;pos<bytes.length;) {
    const n=bytes.readUInt32BE(pos), kind=bytes.toString('ascii',pos+4,pos+8), data=bytes.subarray(pos+8,pos+8+n);
    if(kind==='IHDR') {
      w=data.readUInt32BE(0);h=data.readUInt32BE(4);
      if(data[8]!==8||data[9]!==6||data[12]!==0||w*h>16000000) throw Error('Bounded RGBA required');
    }
    if(kind==='IDAT') parts.push(data);
    pos+=n+12;
    if(kind==='IEND') break;
  }
  const stride=w*4, raw=zlib.inflateSync(Buffer.concat(parts),{maxOutputLength:(stride+1)*h});
  if(raw.length!==(stride+1)*h) throw Error('Wrong raster length');
  const pixels=Buffer.alloc(w*h*4);
  for(let y=0;y<h;y++) for(let x=0;x<stride;x++) {
    const f=raw[y*(stride+1)], i=y*stride+x;
    if(f>4) throw Error('Wrong filter');
    const a=x>=4?pixels[i-4]:0,b=y?pixels[i-stride]:0,c=y&&x>=4?pixels[i-stride-4]:0;
    const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);
    const pred=[0,a,b,Math.floor((a+b)/2),pa<=pb&&pa<=pc?a:pb<=pc?b:c][f];
    pixels[i]=(raw[y*(stride+1)+x+1]+pred)&255;
  }
  return {width:w,height:h,pixels};
}
const old=media.decode(oldBytes), paint=rgba(pigment), out={...old,pixels:Buffer.from(old.pixels)};
let minX=paint.width,minY=paint.height,maxX=0,maxY=0;
for(let y=0;y<paint.height;y++) for(let x=0;x<paint.width;x++) {
  if(paint.pixels[(y*paint.width+x)*4+3]>15) {
    minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);
  }
}
const box=[870,180,150,52], crop=[minX,minY,maxX-minX+1,maxY-minY+1];
let changed=0;
for(let dy=0;dy<box[3];dy++) for(let dx=0;dx<box[2];dx++) {
  const sums=[0,0,0];let coverage=0,count=0;
  const x0=Math.floor(crop[0]+dx*crop[2]/box[2]),x1=Math.floor(crop[0]+(dx+1)*crop[2]/box[2]);
  const y0=Math.floor(crop[1]+dy*crop[3]/box[3]),y1=Math.floor(crop[1]+(dy+1)*crop[3]/box[3]);
  for(let y=y0;y<y1;y++) for(let x=x0;x<x1;x++) {
    count++;
    const i=(y*paint.width+x)*4,[r,g,b,a]=paint.pixels.subarray(i,i+4);
    if(!a || (r>180&&g>175&&b>150)) continue; // omit chalk tallies to avoid numeral-like marks
    const color=r>180&&g>175&&b>150?[218,202,160]:r>g*1.35?[154,57,27]:r>135&&g>90?[181,121,35]:[37,28,21];
    coverage+=a/255;
    for(let c=0;c<3;c++) sums[c]+=color[c]*a/255;
  }
  if(!coverage) continue;
  const a=.76*coverage/count,i=((box[1]+dy)*old.width+box[0]+dx)*3;
  for(let c=0;c<3;c++) out.pixels[i+c]=Math.round(old.pixels[i+c]*(1-a)+sums[c]/coverage*a);
  if(!out.pixels.subarray(i,i+3).equals(old.pixels.subarray(i,i+3))) changed++;
}
let outside=0;
for(let y=0;y<old.height;y++) for(let x=0;x<old.width;x++) {
  if(x>=box[0]&&x<box[0]+box[2]&&y>=box[1]&&y<box[1]+box[3]) continue;
  const i=(y*old.width+x)*3;
  if(!old.pixels.subarray(i,i+3).equals(out.pixels.subarray(i,i+3))) outside++;
}
if(outside||changed<500||changed>8000) throw Error('Preservation failure');
const png=media.encode(out),jpg=media.thumbnail(out);
if(jpg.length>100000||!media.decode(png).pixels.equals(out.pixels)) throw Error('Format failure');
fs.writeFileSync(target,png,{flag:'wx'});
fs.rmSync('artifacts/line-3/wall.png',{force:true});
fs.symlinkSync('wall-v20.png','artifacts/line-3/wall.png');
fs.writeFileSync('dist/line-3/37.jpg',jpg,{flag:'wx'});
const result={source,source_sha256:hash(oldBytes),generated_sha256:hash(pigment),output:target,
 output_sha256:hash(png),patch_xywh:box,changed_pixels:changed,changed_pixels_outside_patch:outside,
 png_dimensions:[old.width,old.height],png_format:'RGB PNG',png_bytes:png.length,
 jpeg_dimensions:[512,512],jpeg_format:'JPEG',jpeg_bytes:jpg.length,
 method:'Imagegen transparent pigment, alpha area averaging, chalk-tally omission and earth-pigment mapping onto untouched ancestor.'};
fs.writeFileSync('line-3/asset-build/preservation-37.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
fs.unlinkSync(pigmentPath);
console.log(JSON.stringify(result,null,2));
