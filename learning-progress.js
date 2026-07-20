export function flowerStage(item){
  return Math.min(3,Math.floor((item.mastery||0)*4.01));
}

export function isLearned(item){
  return flowerStage(item)===3&&item.state==='mastered';
}

export function packCardCounts(pack,progress){
  let ids=new Set((pack.items||[]).map(item=>item.item_id));
  let items=(progress?.items||[]).filter(item=>ids.has(item.item_id));
  return {
    total:ids.size,
    seen:new Set(items.filter(item=>item.last_seen_at).map(item=>item.item_id)).size,
    complete:new Set(items.filter(isLearned).map(item=>item.item_id)).size
  };
}
