import test from 'node:test';
import assert from 'node:assert/strict';
import {flowerStage,isLearned,packCardCounts} from '../learning-progress.js';

test('only mastered, fully bloomed items are learned',()=>{
  assert.equal(isLearned({mastery:0,state:'learning'}),false);
  assert.equal(isLearned({mastery:.74,state:'mastered'}),false);
  assert.equal(isLearned({mastery:.8,state:'learning'}),false);
  assert.equal(flowerStage({mastery:.8}),3);
  assert.equal(isLearned({mastery:.8,state:'mastered'}),true);
});

test('pack complete count excludes cards that have merely been seen or introduced',()=>{
  let pack={items:[{item_id:'seen'},{item_id:'introduced'},{item_id:'learned'}]};
  let progress={items:[
    {item_id:'seen',last_seen_at:'2026-07-20T00:00:00Z',mastery:0,state:'learning'},
    {item_id:'introduced',last_seen_at:'2026-07-20T00:00:00Z',lesson_status:'completed',mastery:.18,state:'learning'},
    {item_id:'learned',last_seen_at:'2026-07-20T00:00:00Z',lesson_status:'completed',mastery:.8,state:'mastered'}
  ]};

  assert.deepEqual(packCardCounts(pack,progress),{total:3,seen:3,complete:1});
});
