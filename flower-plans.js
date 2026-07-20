export function shuffle(values, random=Math.random){
  let result=[...values];
  for(let i=result.length-1;i>0;i--){let j=Math.floor(random()*(i+1));[result[i],result[j]]=[result[j],result[i]]}
  return result
}

const sample=(values,count,random)=>shuffle(values,random).slice(0,count)

export function createFlowerPlan(items,flowers,selectionType='balanced',random=Math.random,selectedSpecies){
  if(!items.length)throw new Error('A flower plan needs at least one learning item')
  if(!flowers.length)throw new Error('No flower sprites are available')
  let species=selectedSpecies?.filter(id=>flowers.includes(id))||[]
  if(selectionType==='balanced'&&!species.length)species=sample(flowers,Math.min(flowers.length,1+Math.floor(random()*5)),random)
  if(selectionType==='maximum_variety')species=[...flowers]
  let sequence=[]
  if(selectionType==='random_mix')sequence=items.map(()=>flowers[Math.floor(random()*flowers.length)])
  else if(selectionType==='maximum_variety')while(sequence.length<items.length)sequence.push(...shuffle(flowers,random))
  else {
    let base=Math.floor(items.length/species.length),remainder=items.length%species.length
    species.forEach((id,index)=>sequence.push(...Array(base+(index<remainder?1:0)).fill(id)))
    sequence=shuffle(sequence,random)
  }
  sequence=sequence.slice(0,items.length)
  return {selection_type:selectionType,species:[...new Set(sequence)],assignments:Object.fromEntries(items.map((item,index)=>[item.item_id,sequence[index]]))}
}

export function createFlowerChoices(items,flowers,random=Math.random){
  let special=random()<.1,types=Array(5).fill('balanced')
  if(special){let first=Math.floor(random()*5),second=(first+1+Math.floor(random()*4))%5;types[first]='random_mix';types[second]='maximum_variety'}
  return types.map(type=>createFlowerPlan(items,flowers,type,random))
}

export function expandFlowerPlan(plan,items,flowers,random=Math.random){
  let missing=items.filter(item=>!plan.assignments[item.item_id])
  if(!missing.length)return plan
  let eligible=plan.selection_type==='balanced'&&plan.species?.length?plan.species:flowers
  let addition=createFlowerPlan(missing,eligible,plan.selection_type||'balanced',random,eligible)
  Object.assign(plan.assignments,addition.assignments)
  plan.species=[...new Set([...plan.species||[],...addition.species])]
  return plan
}
