// Rebuild gathering previews from their original full walls at quality 70.
// Build-time only: Node standard library and the accepted local JPEG encoder.
// No full wall, line file, metadata record, environment or network is changed.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const media = require('../line-1/media/finish-wall.cjs');
const jpeg = require('../line-1/media/jpeg-encoder.cjs');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
function thumbnail(image) {
  const size = 512, data = Buffer.alloc(size*size*4,255);
  for(let y=0;y<size;y++) for(let x=0;x<size;x++) {
    const x0=x*image.width/size,x1=(x+1)*image.width/size;
    const y0=y*image.height/size,y1=(y+1)*image.height/size;
    const sums=[0,0,0]; let area=0;
    for(let sy=Math.floor(y0);sy<Math.ceil(y1);sy++) for(let sx=Math.floor(x0);sx<Math.ceil(x1);sx++) {
      const weight=(Math.min(x1,sx+1)-Math.max(x0,sx))*(Math.min(y1,sy+1)-Math.max(y0,sy));
      area+=weight;
      for(let c=0;c<3;c++) sums[c]+=image.pixels[(sy*image.width+sx)*3+c]*weight;
    }
    for(let c=0;c<3;c++) data[(y*size+x)*4+c]=Math.round(sums[c]/area);
  }
  return jpeg({width:size,height:size,data},70).data;
}
const walls=new Map();
for(const name of fs.readdirSync('artifacts/gathering')) {
  if(!/^wall-v\d+\.png$/.test(name))continue;
  const file='artifacts/gathering/'+name;
  walls.set(sha(fs.readFileSync(file)),file);
}
const rows=[];
for(const name of fs.readdirSync('dist/gathering').sort()) {
  if(!/^\d\d\.json$/.test(name))continue;
  const record=JSON.parse(fs.readFileSync('dist/gathering/'+name));
  if(record.name==='Not painted yet')continue;
  const source=walls.get(record.image.split('/').pop());
  // Earliest source is not supplied here; retain its original preview.
  if(!source)continue;
  const file='dist/gathering/'+name.replace('.json','.jpg');
  const before=fs.readFileSync(file),after=thumbnail(media.decode(fs.readFileSync(source)));
  if(after.length>=before.length || after.length>100000)continue;
  fs.writeFileSync(file,after);
  rows.push({path:file,source,source_sha256:record.image.split('/').pop(),
    before_sha256:sha(before),after_sha256:sha(after),before_bytes:before.length,
    after_bytes:after.length,width:512,height:512,format:'JPEG',quality:70});
  console.log(file+': '+before.length+' -> '+after.length);
}
if(rows.length || !fs.existsSync('gathering/preview-compression-39.json'))
fs.writeFileSync('gathering/preview-compression-39.json',JSON.stringify({
  method:'Area-average original full PNG to 512 square, JPEG quality 70; no additional resize or full-wall change.',
  limitation:'JPEG encoding is lossy; fine pigment and rock texture soften. Full walls and content-addressed records are unchanged.',
  previews:rows,saved_bytes:rows.reduce((sum,r)=>sum+r.before_bytes-r.after_bytes,0)
},null,2)+'\n');
