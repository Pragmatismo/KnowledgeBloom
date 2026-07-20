import test from 'node:test'
import assert from 'node:assert/strict'
import {createFlowerPlan,createFlowerChoices,expandFlowerPlan} from '../flower-plans.js'

const items=n=>Array.from({length:n},(_,i)=>({item_id:`item_${i}`}))
const flowers=['rose','poppy','blue','yellow','purple']
const steady=()=>.42

test('balanced plans assign every item once with counts differing by no more than one',()=>{
  let plan=createFlowerPlan(items(23),flowers,'balanced',steady,['rose','poppy','blue','yellow'])
  assert.equal(Object.keys(plan.assignments).length,23)
  let counts=Object.values(plan.assignments).reduce((all,id)=>(all[id]=(all[id]||0)+1,all),{})
  assert.ok(Math.max(...Object.values(counts))-Math.min(...Object.values(counts))<=1)
})

test('maximum variety uses every species before a repeat',()=>{
  let plan=createFlowerPlan(items(7),flowers,'maximum_variety',steady)
  assert.equal(new Set(Object.values(plan.assignments).slice(0,5)).size,5)
})

test('choice generator always returns five complete choices',()=>{
  let choices=createFlowerChoices(items(9),flowers,steady)
  assert.equal(choices.length,5)
  choices.forEach(plan=>assert.equal(Object.keys(plan.assignments).length,9))
})

test('pack expansion preserves old assignments',()=>{
  let plan=createFlowerPlan(items(3),flowers,'balanced',steady,['rose','blue']),before={...plan.assignments}
  expandFlowerPlan(plan,items(5),flowers,steady)
  assert.deepEqual(Object.fromEntries(Object.entries(plan.assignments).slice(0,3)),before)
  assert.equal(Object.keys(plan.assignments).length,5)
})
