const board=document.querySelector('#board'),lesson=document.querySelector('#lesson'),status=document.querySelector('#status'),progressLabel=document.querySelector('#progress-label'),progressBar=document.querySelector('#progress-bar'),metrics=document.querySelector('.metrics');
const metric={turns:document.querySelector('#turns'),flips:document.querySelector('#flips'),streak:document.querySelector('#streak'),score:document.querySelector('#score')};
let session=null,cards=[],first=null,locked=false,matched=0,turns=0,flips=0,misses=0,streak=0,score=0,startedAt=0,submitted=false,removeTimer=null;
const shuffle=values=>{let result=[...values];for(let i=result.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[result[i],result[j]]=[result[j],result[i]]}return result};
const key=item=>`${item.pack_id}:${item.item_id}`;
const element=(tag,props={},...children)=>{let node=document.createElement(tag);for(let [name,value] of Object.entries(props)){if(name==='class')node.className=value;else if(name.startsWith('on'))node.addEventListener(name.slice(2).toLowerCase(),value);else if(name.includes('-'))node.setAttribute(name,value);else node[name]=value}node.append(...children.filter(value=>value!=null));return node};
const sameImage=(a,b)=>{
  let aQuestion=a.item.content?.question||{},bQuestion=b.item.content?.question||{};
  return a.side!==b.side&&!aQuestion.text?.trim()&&!bQuestion.text?.trim()&&aQuestion.image&&aQuestion.image===bQuestion.image;
};

function start(value){
  session=value;
  if(!Array.isArray(session.items)||!session.items.length)return showError('No compatible memory pairs were supplied.');
  let introductions=session.items.filter(item=>item.interaction_type==='introduction');
  if(introductions.length)return startLesson(introductions);
  beginRound();
}

function beginRound(){
  cards=shuffle(session.items.flatMap(item=>[
    {id:`${key(item)}:question`,side:'question',item},
    {id:`${key(item)}:answer`,side:'answer',item}
  ]));
  let columns=cards.length<=8?4:cards.length<=12?4:cards.length<=16?4:5;
  board.style.setProperty('--columns',columns);
  board.replaceChildren(...cards.map(renderCard));
  lesson.hidden=true;metrics.hidden=false;status.hidden=false;board.hidden=false;
  progressLabel.textContent='Your memory board is ready';
  status.textContent="Find each question's answer.";
  startedAt=Date.now();
  update();
}

function startLesson(items){
  let index=0;
  board.hidden=true;metrics.hidden=true;status.hidden=true;lesson.hidden=false;
  const show=()=>{
    let item=items[index],last=index===items.length-1,content=item.content||{},question=content.question||{},answer=content.answer||{};
    progressLabel.textContent=`Learning new card ${index+1} of ${items.length}`;
    progressBar.style.width=`${(index+1)/items.length*100}%`;
    lesson.replaceChildren(
      element('span',{class:'eyebrow'},`New card ${index+1} of ${items.length}`),
      element('h2',{},index===0?'This round will involve these new cards…':'Here is another new card…'),
      element('p',{class:'lesson-intro'},'Take a moment to learn the question and its matching answer.'),
      element('div',{class:'teaching-card'},
        element('div',{class:'teaching-side'},element('span',{class:'side-label'},'Question'),...teachingContent(question,'Question')),
        element('span',{class:'lesson-arrow','aria-hidden':'true'},'→'),
        element('div',{class:'teaching-side answer-side'},element('span',{class:'side-label'},'Answer'),...teachingContent(answer,'Answer'))
      ),
      element('button',{class:'primary',type:'button',onclick:()=>{if(last)beginRound();else{index++;show()}}},last?'Start round':'Next new card')
    );
    lesson.querySelector('.primary').focus();
  };
  show();
}

function teachingContent(content,fallback){
  let nodes=[];
  if(content.image)nodes.push(element('img',{class:'lesson-media',src:content.image,alt:content.text||''}));
  if(content.audio)nodes.push(element('audio',{class:'lesson-media',src:content.audio,controls:true,preload:'metadata','aria-label':`${fallback} audio`}));
  if(content.video)nodes.push(element('video',{class:'lesson-media',src:content.video,controls:true,preload:'metadata','aria-label':`${fallback} video`}));
  nodes.push(element('strong',{class:'lesson-text'},content.text||fallback));
  return nodes;
}

function renderCard(card){
  let button=element('button',{class:'memory-card',type:'button','aria-label':'Face-down memory card',onclick:()=>flip(card)});
  button.dataset.cardId=card.id;
  button.append(element('span',{class:'card-inner'},element('span',{class:'card-face card-back','aria-hidden':'true'}),element('span',{class:'card-face card-front'},...faceContent(card))));
  card.node=button;
  return button;
}

function faceContent(card){
  let content=card.item.content?.[card.side]||{},nodes=[element('span',{class:'side-label'},card.side==='question'?'Question':'Answer')];
  if(content.image)nodes.push(element('img',{class:'card-media',src:content.image,alt:content.text||''}));
  if(content.audio)nodes.push(element('audio',{class:'card-media',src:content.audio,controls:true,preload:'metadata','aria-label':`${card.side} audio`}));
  if(content.video)nodes.push(element('video',{class:'card-media',src:content.video,controls:true,preload:'metadata','aria-label':`${card.side} video`}));
  if(content.text)nodes.push(element('span',{class:'card-text'},content.text));
  if(nodes.length===1)nodes.push(element('span',{class:'card-text'},card.side==='question'?'Question':'Answer'));
  return nodes;
}

function flip(card){
  if(locked||card===first||card.matched||card.node.classList.contains('revealed'))return;
  card.node.classList.add('revealed');
  card.node.setAttribute('aria-label',`${card.side}: ${card.item.content?.[card.side]?.text||'media card'}`);
  flips++;
  if(!first){first=card;status.textContent='Now find its matching card.';return update()}
  turns++;
  let earlier=first;first=null;locked=true;
  if(isMatch(earlier,card))completePair(earlier,card);else hidePair(earlier,card);
  update();
}

function isMatch(a,b){return (a.side!==b.side&&key(a.item)===key(b.item))||sameImage(a,b)}

function completePair(a,b){
  a.matched=b.matched=true;
  a.node.classList.add('matched');b.node.classList.add('matched');
  matched++;streak++;score+=100+Math.max(0,(streak-1)*20);
  status.textContent=streak>1?`${streak} matches in a row!`:'A perfect pair!';
  removeTimer=setTimeout(()=>{
    a.node.classList.add('removing');b.node.classList.add('removing');
    setTimeout(()=>{a.node.classList.add('removed');b.node.classList.add('removed')},350);
    locked=false;removeTimer=null;update();
    if(matched===session.items.length)finish();
  },650);
}

function hidePair(a,b){
  misses++;streak=0;score=Math.max(0,score-5);status.textContent='Take a good look — these cards do not match.';
  setTimeout(()=>{
    for(let card of [a,b]){card.node.classList.remove('revealed');card.node.setAttribute('aria-label','Face-down memory card')}
    locked=false;status.textContent='Try another pair.';update();
    a.node.focus();
  },950);
}

function update(){
  let total=session?.items?.length||0;
  progressLabel.textContent=`${matched} of ${total} pairs found`;
  progressBar.style.width=`${total?matched/total*100:0}%`;
  metric.turns.textContent=turns;metric.flips.textContent=flips;metric.streak.textContent=streak;metric.score.textContent=score;
}

function finish(){
  locked=true;
  let results=session.items.map(item=>({pack_id:item.pack_id,item_id:item.item_id,interaction_type:item.interaction_type,attempts:[{correct:true}],first_attempt_correct:true,finished_correctly:true,deferred:false,...(item.interaction_type==='introduction'?{introduction:{teaching_card_shown:true,attention_check_completed:true}}:{})}));
  let summary={items_presented:results.length,new_items_introduced:results.filter(result=>result.interaction_type==='introduction').length,first_attempt_correct:results.length,items_finished_correctly:results.length,items_deferred:0};
  let result={result_schema_version:'1.0',session_id:session.session_id,game_id:session.game_id,user_id:session.user_id,round_completed:true,ended_at:new Date().toISOString(),summary,results,game_metrics:{pairs_found:matched,turns,flips,unmatched_pairs:misses,score,time_seconds:Math.round((Date.now()-startedAt)/1000)}};
  submitted=true;
  parent.postMessage({type:'knowledge-bloom:result',result},location.origin);
  showSummary(false);
}

function showSummary(accepted){
  board.hidden=true;lesson.hidden=true;metrics.hidden=true;status.hidden=true;
  let summary=document.querySelector('#summary');summary.hidden=false;
  summary.replaceChildren(element('span',{class:'eyebrow'},accepted?'Saved to your garden':'Round complete'),element('h2',{},'Round Complete'),element('div',{class:'summary-grid'},stat(`${matched} / ${session.items.length}`,'Pairs found'),stat(turns,'Turns taken'),stat(misses,'Unmatched pairs'),stat(score,'Score')),element('p',{class:'save-note'},accepted?'Every completed pair was sent as one successful learning interaction. Positional guesses did not count as wrong answers.':'Saving your completed pairs…'),element('button',{class:'primary',type:'button',disabled:!accepted,onclick:()=>parent.postMessage({type:'knowledge-bloom:close'},location.origin)},'Return to the garden'));
}

function stat(value,label){return element('div',{},element('strong',{},String(value)),label)}
function showError(message){board.replaceChildren(element('p',{class:'summary'},message));status.textContent='This round could not begin.'}

addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==parent)return;
  if(event.data?.type==='knowledge-bloom:session'&&!session)start(event.data.session);
  if(event.data?.type==='knowledge-bloom:result-ack'&&submitted){
    if(event.data.accepted)showSummary(true);
    else document.querySelector('#summary').replaceChildren(element('h2',{},'We could not save this round'),element('p',{class:'save-note'},'Your results were not applied. Please return to the garden and try again.'),element('button',{class:'primary',type:'button',onclick:()=>parent.postMessage({type:'knowledge-bloom:close'},location.origin)},'Return to the garden'));
  }
});
document.querySelector('#leave').addEventListener('click',()=>{if(confirm('Leave this round? Only a completed board can be saved.'))parent.postMessage({type:'knowledge-bloom:close',round_completed:false},location.origin)});
parent.postMessage({type:'knowledge-bloom:ready'},location.origin);
