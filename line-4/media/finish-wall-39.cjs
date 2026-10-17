// Add only generated pigment to bare inherited stone. No network or secrets.
const fs=require('node:fs'), zlib=require('node:zlib'), crypto=require('node:crypto');
const {decode,encode,thumbnail}=require('../../line-1/media/finish-wall.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function generated(bytes){
  if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw Error('PNG required');
  let width,height,channels,parts=[];
  for(let p=8;p<bytes.length;){
    const n=bytes.readUInt32BE(p),t=bytes.toString('ascii',p+4,p+8),v=bytes.subarray(p+8,p+8+n);
    if(t==='IHDR'){
      width=v.readUInt32BE(0);height=v.readUInt32BE(4);channels=v[9]===2?3:v[9]===6?4:0;
      if(width>4096||height>4096||!width||!height||!channels||v[8]!==8||v[12])throw Error('unsupported generated PNG');
    }
    if(t==='IDAT')parts.push(v);
    p+=n+12;if(t==='IEND')break;
  }
  const stride=width*channels,raw=zlib.inflateSync(Buffer.concat(parts),{maxOutputLength:(stride+1)*height});
  if(raw.length!==(stride+1)*height)throw Error('bad raster');
  const pixels=Buffer.alloc(stride*height);
  for(let y=0;y<height;y++)for(let x=0;x<stride;x++){
    const i=y*stride+x,f=raw[y*(stride+1)];if(f>4)throw Error('bad filter');
    const a=x>=channels?pixels[i-channels]:0,b=y?pixels[i-stride]:0,c=y&&x>=channels?pixels[i-stride-channels]:0;
    const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);
    const predictor=[0,a,b,Math.floor((a+b)/2),pa<=pb&&pa<=pc?a:pb<=pc?b:c][f];
    pixels[i]=(raw[y*(stride+1)+x+1]+predictor)&255;
  }
  return {width,height,channels,pixels};
}
const ancestorBytes=fs.readFileSync('artifacts/line-4/wall-v19.png');
const record=JSON.parse(fs.readFileSync('dist/line-4/38.json'));
if(record.image!=='https://api.imd.fun/artifacts/'+sha(ancestorBytes))throw Error('ancestor hash mismatch');
if(!fs.readFileSync('artifacts/line-4/wall.png').equals(ancestorBytes))throw Error('continuing wall differs');
if(fs.existsSync('dist/line-4/39.json'))throw Error('record already exists');
const old=decode(ancestorBytes),mark=generated(fs.readFileSync('artifacts/line-4/wall-v20.png'));
const out={...old,pixels:Buffer.from(old.pixels)};
const box=[150,210,210,65];let changed=0;
// The input is an isolated motif on white. Reject its background and map
// selected opaque stroke samples onto three earth pigments before blending.
function pigment(x,y){
  const i=(y*mark.width+x)*mark.channels,r=mark.pixels[i],g=mark.pixels[i+1],b=mark.pixels[i+2];
  if(mark.channels===4&&mark.pixels[i+3]<240)return null;
  if(r<125&&g<120&&b<110)return [46,36,26];
  if(r>g*1.30&&g>b*1.12&&r>90&&g<170)return [157,70,34];
  if(r>g*1.08&&g>b*1.65&&r>125&&g<195)return [187,130,44];
  return null;
}
let minX=mark.width,minY=mark.height,maxX=0,maxY=0;
for(let y=0;y<mark.height;y++)for(let x=0;x<mark.width;x++)if(pigment(x,y)){
 minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);
}
if(maxX<=minX||maxY<=minY)throw Error('no generated pigment');
const scale=Math.min(box[2]/(maxX-minX+1),box[3]/(maxY-minY+1));
const w=(maxX-minX+1)*scale,h=(maxY-minY+1)*scale;
for(let y=0;y<box[3];y++)for(let x=0;x<box[2];x++){
 let count=0,sums=[0,0,0];
 for(let sy=0;sy<4;sy++)for(let sx=0;sx<4;sx++){
   const mx=(x+(sx+.5)/4-(box[2]-w)/2)/scale+minX;
   const my=(y+(sy+.5)/4-(box[3]-h)/2)/scale+minY;
   if(mx<minX||my<minY||mx>maxX||my>maxY)continue;
   const c=pigment(Math.floor(mx),Math.floor(my));if(!c)continue;
   count++;for(let k=0;k<3;k++)sums[k]+=c[k];
 }
 if(!count)continue;
 const j=((box[1]+y)*old.width+box[0]+x)*3;
 const light=(old.pixels[j]+old.pixels[j+1]+old.pixels[j+2])/765;
 const opacity=count/16*(.70+.16*light);
 for(let k=0;k<3;k++)out.pixels[j+k]=Math.round(old.pixels[j+k]*(1-opacity)+sums[k]/count*opacity);
 if(!out.pixels.subarray(j,j+3).equals(old.pixels.subarray(j,j+3)))changed++;
}
let outside=0;
for(let y=0;y<old.height;y++)for(let x=0;x<old.width;x++){
 if(x>=box[0]&&x<box[0]+box[2]&&y>=box[1]&&y<box[1]+box[3])continue;
 const i=(y*old.width+x)*3;
 if(!out.pixels.subarray(i,i+3).equals(old.pixels.subarray(i,i+3)))outside++;
}
if(outside||changed<200)throw Error('preservation or pigment check failed');
const png=encode(out),jpg=thumbnail(out);
if(!decode(png).pixels.equals(out.pixels)||jpg.length>100000)throw Error('output codec check failed');
fs.writeFileSync('artifacts/line-4/wall-v20.png',png);
fs.unlinkSync('artifacts/line-4/wall.png');
fs.linkSync('artifacts/line-4/wall-v20.png','artifacts/line-4/wall.png');
fs.writeFileSync('artifacts/line-4/39.jpg',jpg);
fs.linkSync('artifacts/line-4/39.jpg','dist/line-4/39.jpg');
const next={name:'The Ordered Stones',image:'https://api.imd.fun/artifacts/'+sha(png),attributes:[
 {trait_type:'Cave',value:'Lava'},{trait_type:'Wall',value:'Line 4'},{trait_type:'Number',value:39},
 {trait_type:'Left behind',value:'TupleCheck'},
 {trait_type:'Meaning',value:'Three cups hold distinct stones in order, as a tuple checks each position.'},
 {trait_type:'One thing',value:'Detect breaking OpenAPI changes'}]};
fs.writeFileSync('dist/line-4/39.json',JSON.stringify(next,null,2)+'\n');
const review={ancestor_sha256:sha(ancestorBytes),sha256:sha(png),dimensions:[old.width,old.height],format:'RGB PNG',
 wall:'artifacts/line-4/wall-v20.png',canonical_wall:'artifacts/line-4/wall.png',preview:'dist/line-4/39.jpg',
 preview_format:'JPEG',preview_dimensions:[512,512],preview_bytes:jpg.length,addition_bounds:box,
 changed_pixels:changed,pixels_changed_outside_addition:outside,png_roundtrip_passed:true,
 method:'Installed image tool generated isolated pigment on white. White discarded; selected strokes mapped to ochre and charcoal and blended onto exact inherited stone.',
 visual_review:'Pending final inspection.',unmet_visual_requirements:[],prompt_record:'line-4/MARK-39.md'};
fs.writeFileSync('line-4/review-39.json',JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify(review,null,2));
