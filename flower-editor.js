const panel=document.querySelector('#flower-editor');
const canvas=document.querySelector('#flower-alignment-canvas'),context=canvas.getContext('2d',{willReadFrequently:true});
const select=document.querySelector('#flower-editor-select'),nameInput=document.querySelector('#flower-editor-name');
const widthInput=document.querySelector('#flower-crop-width'),heightInput=document.querySelector('#flower-crop-height');
const status=document.querySelector('#flower-editor-status');
let source=null,sourceUrl='',frame=0,frameWidth=0,frameHeight=0,view={scale:1,x:0,y:0};
let crops=[],drag=null;
const labels=['Seedling · watered','Sprout · watered','Growing · watered','Bloom · watered','Seedling · unwatered','Sprout · unwatered','Growing · unwatered','Bloom · unwatered'];

function imageFrom(url){return new Promise((resolve,reject)=>{let image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error('The selected image could not be opened.'));image.src=url})}
function refreshChoices(selected=''){fetch('/api/catalogue').then(r=>r.json()).then(data=>{select.replaceChildren(...data.flowers.map(f=>new Option(f.id,f.image,f.image===selected,f.image===selected)));if(!selected&&select.value)choose(select.value)})}
function defaultCrop(index){return{x:(index%4)*frameWidth,y:Math.floor(index/4)*frameHeight,w:frameWidth,h:frameHeight}}
async function choose(url,displayName=''){
 try{source=await imageFrom(url);sourceUrl=url;frameWidth=Math.floor(source.naturalWidth/4);frameHeight=Math.floor(source.naturalHeight/2);if(!frameWidth||!frameHeight)throw new Error('Image is too small.');crops=Array.from({length:8},(_,i)=>defaultCrop(i));frame=0;nameInput.value=(displayName||url.split('/').pop().replace(/\.[^.]+$/,'')).replace(/[^A-Za-z0-9_-]/g,'_');status.textContent='';draw()}catch(error){status.textContent=error.message}
}
function cropOnCanvas(crop=crops[frame]){return{x:view.x+crop.x*view.scale,y:view.y+crop.y*view.scale,w:crop.w*view.scale,h:crop.h*view.scale}}
function draw(){
 if(!source)return;
 context.clearRect(0,0,canvas.width,canvas.height);
 view.scale=Math.min((canvas.width-32)/source.naturalWidth,(canvas.height-32)/source.naturalHeight);
 view.x=(canvas.width-source.naturalWidth*view.scale)/2;view.y=(canvas.height-source.naturalHeight*view.scale)/2;
 context.imageSmoothingEnabled=false;context.drawImage(source,view.x,view.y,source.naturalWidth*view.scale,source.naturalHeight*view.scale);
 let box=cropOnCanvas();
 context.save();context.fillStyle='#15201699';context.beginPath();context.rect(view.x,view.y,source.naturalWidth*view.scale,source.naturalHeight*view.scale);context.rect(box.x,box.y,box.w,box.h);context.fill('evenodd');context.strokeStyle='#e02732';context.lineWidth=3;context.strokeRect(box.x,box.y,box.w,box.h);
 context.fillStyle='#fff';context.strokeStyle='#e02732';for(let [x,y] of [[box.x,box.y],[box.x+box.w/2,box.y],[box.x+box.w,box.y],[box.x,box.y+box.h/2],[box.x+box.w,box.y+box.h/2],[box.x,box.y+box.h],[box.x+box.w/2,box.y+box.h],[box.x+box.w,box.y+box.h]]){context.fillRect(x-5,y-5,10,10);context.strokeRect(x-5,y-5,10,10)}context.restore();
 widthInput.value=Math.round(crops[frame].w);heightInput.value=Math.round(crops[frame].h);
 document.querySelector('#flower-frame-label').textContent=labels[frame];document.querySelector('#flower-frame-count').textContent=`Frame ${frame+1} of 8`;document.querySelector('#flower-frame-previous').disabled=frame===0;document.querySelector('#flower-frame-next').disabled=frame===7;
}
function moveFrame(by){frame=Math.max(0,Math.min(7,frame+by));draw()}
function clampCrop(crop){crop.w=Math.max(1,Math.min(source.naturalWidth,crop.w));crop.h=Math.max(1,Math.min(source.naturalHeight,crop.h));crop.x=Math.max(0,Math.min(source.naturalWidth-crop.w,crop.x));crop.y=Math.max(0,Math.min(source.naturalHeight-crop.h,crop.y));return crop}
function setCropSize(){if(!source)return;let crop=crops[frame],w=Number(widthInput.value),h=Number(heightInput.value);if(!Number.isFinite(w)||!Number.isFinite(h))return;let cx=crop.x+crop.w/2,cy=crop.y+crop.h/2;clampCrop(Object.assign(crop,{w:Math.round(w),h:Math.round(h),x:cx-w/2,y:cy-h/2}));draw()}
function buildSheet(){let cellWidth=Math.max(...crops.map(c=>Math.ceil(c.w))),cellHeight=Math.max(...crops.map(c=>Math.ceil(c.h))),output=document.createElement('canvas');output.width=cellWidth*4;output.height=cellHeight*2;let c=output.getContext('2d');c.imageSmoothingEnabled=false;crops.forEach((crop,n)=>c.drawImage(source,crop.x,crop.y,crop.w,crop.h,(n%4)*cellWidth+(cellWidth-crop.w)/2,Math.floor(n/4)*cellHeight+cellHeight-crop.h,crop.w,crop.h));return output}
function pointer(e){let r=canvas.getBoundingClientRect();return{x:(e.clientX-r.left)*canvas.width/r.width,y:(e.clientY-r.top)*canvas.height/r.height}}
function hitMode(p,box){let near=(a,b)=>Math.abs(a-b)<=10,left=near(p.x,box.x),right=near(p.x,box.x+box.w),top=near(p.y,box.y),bottom=near(p.y,box.y+box.h),withinX=p.x>=box.x-10&&p.x<=box.x+box.w+10,withinY=p.y>=box.y-10&&p.y<=box.y+box.h+10;if(top&&withinX)return left?'nw':right?'ne':'n';if(bottom&&withinX)return left?'sw':right?'se':'s';if(left&&withinY)return'w';if(right&&withinY)return'e';if(p.x>=box.x&&p.x<=box.x+box.w&&p.y>=box.y&&p.y<=box.y+box.h)return'move';return''}
canvas.addEventListener('pointerdown',e=>{if(!source)return;let p=pointer(e),mode=hitMode(p,cropOnCanvas());if(!mode)return;drag={p,mode,start:{...crops[frame]}};canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener('pointermove',e=>{if(!drag)return;let p=pointer(e),dx=(p.x-drag.p.x)/view.scale,dy=(p.y-drag.p.y)/view.scale,c={...drag.start};if(drag.mode==='move'){c.x+=dx;c.y+=dy}else{if(drag.mode.includes('w')){c.x+=dx;c.w-=dx}if(drag.mode.includes('e'))c.w+=dx;if(drag.mode.includes('n')){c.y+=dy;c.h-=dy}if(drag.mode.includes('s'))c.h+=dy}crops[frame]=clampCrop(c);draw()});
canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);
document.querySelector('#open-flower-editor').addEventListener('click',()=>{panel.hidden=false;document.querySelector('#guide').hidden=true;refreshChoices()});document.querySelector('#flower-editor-close').addEventListener('click',()=>panel.hidden=true);select.addEventListener('change',()=>choose(select.value));
document.querySelector('#flower-editor-upload').addEventListener('change',e=>{let file=e.target.files[0];if(!file)return;if(sourceUrl.startsWith('blob:'))URL.revokeObjectURL(sourceUrl);choose(URL.createObjectURL(file),file.name.replace(/\.[^.]+$/,''));e.target.value=''});
document.querySelector('#flower-frame-previous').addEventListener('click',()=>moveFrame(-1));document.querySelector('#flower-frame-next').addEventListener('click',()=>moveFrame(1));document.querySelector('#flower-frame-reset').addEventListener('click',()=>{crops[frame]=defaultCrop(frame);draw()});widthInput.addEventListener('change',setCropSize);heightInput.addEventListener('change',setCropSize);
document.querySelector('#flower-editor-save').addEventListener('click',()=>{let name=nameInput.value.trim();if(!/^[A-Za-z0-9_-]+$/.test(name)){status.textContent='Use only letters, numbers, hyphens and underscores in the name.';return}status.textContent='Saving…';buildSheet().toBlob(async blob=>{try{let response=await fetch('/api/flowers',{method:'POST',headers:{'Content-Type':'image/png','X-Filename':encodeURIComponent(name+'.png')},body:blob});if(!response.ok)throw new Error(await response.text());let saved=await response.json();status.textContent=`Saved ${saved.image} (${saved.width} × ${saved.height}px)`;refreshChoices(saved.image)}catch(error){status.textContent=`Save failed: ${error.message}`}},'image/png')});
