// Keep only the generated pouch on bare left rock; preserve all ancestors.
const fs = require('node:fs');
const crypto = require('node:crypto');
const {decode, encode, thumbnail} = require('./finish-wall.cjs');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const oldBytes = fs.readFileSync('artifacts/line-1/wall.png');
const old = decode(oldBytes);
const edit = decode(fs.readFileSync('artifacts/line-1/wall-v20.png'));
const output = {...old, pixels: Buffer.from(old.pixels)};
const clamp = x => Math.max(0, Math.min(1, x));
function ellipse(x,y,cx,cy,rx,ry) {
  return (1-Math.hypot((x-cx)/rx,(y-cy)/ry))*Math.min(rx,ry);
}
function mask(x,y) {
  const distance = Math.max(ellipse(x,y,100,692,52,47),
                            ellipse(x,y,101,649,25,33),
                            ellipse(x,y,101,623,32,22));
  return clamp(distance/5);
}
let changed=0, protectedPixels=0, outsideChanged=0;
for(let y=0;y<old.height;y++) for(let x=0;x<old.width;x++) {
  const a=mask(x,y), at=(y*old.width+x)*3;
  if(!a) protectedPixels++;
  let differs=false;
  for(let c=0;c<3;c++) {
    output.pixels[at+c]=Math.round(old.pixels[at+c]*(1-a)+edit.pixels[at+c]*a);
    differs ||= output.pixels[at+c] !== old.pixels[at+c];
  }
  if(differs) changed++;
  if(!a && differs) outsideChanged++;
}
if(outsideChanged || changed<1000) throw Error('mask failed');
const png=encode(output), jpg=thumbnail(output);
if(!decode(png).pixels.equals(output.pixels)) throw Error('PNG roundtrip failed');
if(jpg.length>100000) throw Error('JPEG too large');
fs.writeFileSync('artifacts/line-1/wall-v20.png',png);
fs.writeFileSync('artifacts/line-1/wall.png',png);
fs.writeFileSync('dist/line-1/39.jpg',jpg);
const report={previous_sha256:hash(oldBytes),sha256:hash(png),format:'PNG',width:old.width,height:old.height,
 png_bytes:png.length,preview_format:'JPEG',preview_width:512,preview_height:512,preview_bytes:jpg.length,
 changed_pixels:changed,protected_pixels:protectedPixels,outside_mask_changed_pixels:outsideChanged,
 mask:'union of feathered ellipses around generated pouch on bare left rock; x=48..152, y=601..739',
 png_roundtrip_passed:true};
fs.writeFileSync('line-1/media-check-39.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
