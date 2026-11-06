/* Local reading navigation, opt-in progress records, and exact teaching models. */
document.addEventListener('DOMContentLoaded', () => {
  'use strict';
  const course = document.querySelector('#rl-course');
  if (!course) return;
  const lessons = [...course.querySelectorAll('.rl-lesson')];
  const home = course.querySelector('.rl-home');
  const toolbar = course.querySelector('.rl-reader-nav');
  const jump = course.querySelector('#rl-jump');
  const prev = course.querySelector('#rl-prev');
  const next = course.querySelector('#rl-next');
  const allButton = course.querySelector('#rl-show-all');
  const storageKey = 'rl-course-progress-v1';
  let records = {};
  let storageAvailable = true;
  try { records = JSON.parse(localStorage.getItem(storageKey) || '{}'); if (!records || typeof records !== 'object' || Array.isArray(records)) records = {}; } catch { records = {}; storageAvailable = false; }
  let current = 0;
  let continuous = false;
  let mathQueue = Promise.resolve();
  function typeset(elements) {
    mathQueue = mathQueue.then(async () => {
      if (!window.MathJax?.startup?.promise) return;
      await window.MathJax.startup.promise;
      const pending = elements.filter(el => !el.dataset.typeset);
      if (pending.length) { await window.MathJax.typesetPromise(pending); pending.forEach(el => { el.dataset.typeset = 'true'; }); }
    }).catch(error => { console.warn('Formula rendering:', error); });
    return mathQueue;
  }
  function route() {
    const match = location.hash.match(/^#lecture-(\d{2})$/);
    current = match ? Math.max(1, Math.min(65, Number(match[1]))) : 0;
    home.hidden = current !== 0;
    toolbar.hidden = current === 0;
    lessons.forEach(el => { el.hidden = current === 0 || (!continuous && Number(el.dataset.lesson) !== current); });
    if (current) {
      jump.value = String(current); prev.disabled = current === 1; next.disabled = current === 65;
      typeset(continuous ? lessons : [lessons[current - 1]]);
      requestAnimationFrame(() => document.getElementById(`lecture-${String(current).padStart(2,'0')}`)?.scrollIntoView({block:'start',behavior:'instant'}));
    }
    if (!current && (location.hash === '#rl-overview' || location.hash === '#rl-labs')) {
      requestAnimationFrame(() => document.querySelector(location.hash)?.scrollIntoView({block:'start',behavior:'instant'}));
    }
    document.querySelectorAll('.course-outline a').forEach(a => a.setAttribute('aria-current', a.hash === location.hash ? 'location' : 'false'));
  }
  function go(n) { location.hash = `lecture-${String(n).padStart(2,'0')}`; }
  jump.addEventListener('change', () => go(Number(jump.value)));
  prev.addEventListener('click', () => go(Math.max(1,current-1)));
  next.addEventListener('click', () => go(Math.min(65,current+1)));
  allButton.addEventListener('click', () => { continuous = !continuous; allButton.textContent = continuous ? '逐讲阅读' : '连续阅读'; route(); });
  window.addEventListener('hashchange', route);
  const progress = course.querySelector('.rl-progress');
  function showProgress() {
    const count = key => Object.values(records).filter(r => r && r[key] === true).length;
    progress.textContent = `你的记录：已阅读 ${count('read')}/65；能独立解释或推导 ${count('explain')}/65；完成实验 ${count('implement')}/65。`;
  }
  course.querySelectorAll('[data-record]').forEach(box => {
    const id = box.dataset.record;
    const stored = records[id] && typeof records[id] === 'object' ? records[id] : {};
    box.querySelectorAll('[data-status]').forEach(input => { input.checked = stored[input.dataset.status] === true; });
    box.querySelector('textarea').value = typeof stored.note === 'string' ? stored.note : '';
    if (!storageAvailable) box.querySelector('.rl-save-status').textContent = '浏览器存储不可用；记录本次会话后请导出。';
    const save = () => {
      const record = { note: box.querySelector('textarea').value, updated: new Date().toISOString() };
      box.querySelectorAll('[data-status]').forEach(input => { record[input.dataset.status] = input.checked; });
      records[id] = record;
      try { localStorage.setItem(storageKey, JSON.stringify(records)); } catch { box.querySelector('.rl-save-status').textContent = '浏览器存储不可用，请导出记录。'; }
      showProgress();
    };
    box.addEventListener('change',save); box.querySelector('textarea').addEventListener('input',save);
  });
  course.querySelector('#rl-export').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify({course:'robot-reinforcement-learning',version:1,records},null,2)],{type:'application/json'}));
    const a = document.createElement('a'); a.href = url; a.download = 'rl-learning-records.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
  });
  window.addEventListener('beforeprint', () => { lessons.forEach(el => { el.hidden = false; }); typeset(lessons); });
  window.addEventListener('afterprint', route);
  document.querySelector('[data-print-course]')?.addEventListener('click', async event => {
    event.stopImmediatePropagation();
    lessons.forEach(el => { el.hidden = false; });
    await typeset(lessons);
    window.print();
    route();
  }, {capture:true});
  showProgress(); route();

  const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const text = (x,y,s,color='var(--text)',anchor='start') => `<text x="${x}" y="${y}" fill="${color}" font-size="16" text-anchor="${anchor}">${esc(s)}</text>`;
  const line = (x1,y1,x2,y2,color='var(--line)',width=1) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}"/>`;
  function chart(svg,series,xLabel,yLabel,domain) {
    const xs = series.flatMap(s=>s.data.map(d=>d[0])), ys = series.flatMap(s=>s.data.map(d=>d[1]));
    const xmax = Math.max(...xs,1), ymin = domain?.[0] ?? Math.min(0,...ys), ymax = domain?.[1] ?? Math.max(...ys,1);
    const px = x=>65+x/xmax*570, py = y=>211-(y-ymin)/(ymax-ymin||1)*168;
    let out = line(65,43,65,211)+line(65,211,635,211);
    for(let i=0;i<=4;i++){const v=ymin+(ymax-ymin)*i/4;out+=text(55,py(v)+5,v.toFixed(2),'var(--muted)','end')+line(65,py(v),635,py(v));out+=text(px(xmax*i/4),235,(xmax*i/4).toFixed(xmax<2?2:0),'var(--muted)','middle');}
    series.forEach((s,i)=>{out+=`<polyline fill="none" stroke="${s.color}" stroke-width="2.5" points="${s.data.map(d=>`${px(d[0])},${py(d[1])}`).join(' ')}"/>`+text(80+i*255,23,s.name,s.color);});
    out+=text(635,257,xLabel,'var(--muted)','end')+text(8,22,yLabel,'var(--muted)');svg.innerHTML=out;return{px,py};
  }
  function rng(seed){return()=>{seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed/4294967296;};}
  course.querySelectorAll('[data-lab]').forEach(lab=>{
    const input=lab.querySelector('input'),svg=lab.querySelector('svg'),result=lab.querySelector('.rl-lab-result');
    function draw(){const v=Number(input.value);lab.querySelector('output').textContent=v.toFixed(input.step==='1'?0:2);const kind=lab.dataset.lab;
      if(kind==='reward'){
        const loop=Array.from({length:13},(_,t)=>[t,Math.ceil(t/2)]),dock=Array.from({length:13},(_,t)=>[t,t===0?0:t<3?t:2+v]);
        chart(svg,[{name:'门口循环（累计奖励）',color:'var(--warm)',data:loop},{name:'第3步进站（累计奖励）',color:'var(--accent)',data:dock}],'交互步数','累计奖励');result.textContent=`12步循环得6分；进站得${2+v}分。进站后回合终止，后续累计值保持不变。改变奖励会改变被优化的行为。`;
      }else if(kind==='discount'){
        const delayed=8*v**3;svg.innerHTML=line(80,215,620,215)+`<rect x="150" y="${215-4*20}" width="100" height="${4*20}" fill="var(--accent)"/><rect x="410" y="${215-delayed*20}" width="100" height="${delayed*20}" fill="var(--warm)"/>`+text(200,240,'现在4分','var(--text)','middle')+text(460,240,'延后3步得8分','var(--text)','middle')+text(200,120,'4.00','var(--text)','middle')+text(460,Math.max(30,200-delayed*20),delayed.toFixed(2),'var(--text)','middle');result.textContent=`折扣后的延迟收益是8×γ³=${delayed.toFixed(3)}；${delayed>4?'等待更有价值':delayed<4?'即时奖励更有价值':'两者相等'}。γ表示目标的时间权重；这里没有随机生存假设。`;
      }else if(kind==='bandit'){
        function run(eps){const random=rng(42),q=[0,0,0],n=[0,0,0],data=[];let regret=0;for(let t=1;t<=500;t++){let a=random()<eps?Math.floor(random()*3):q.indexOf(Math.max(...q));const r=Number(random()<[.35,.55,.7][a]);n[a]++;q[a]+=(r-q[a])/n[a];regret+=.7-[.35,.55,.7][a];if(t%5===0)data.push([t,regret]);}return data;}
        const greedy=run(0),explore=run(v);chart(svg,[{name:'纯贪心',color:'var(--warm)',data:greedy},{name:'ε-greedy',color:'var(--accent)',data:explore}],'环境步数','累计伪遗憾');result.textContent=`本次固定种子：贪心遗憾${greedy.at(-1)[1].toFixed(1)}，ε-greedy遗憾${explore.at(-1)[1].toFixed(1)}。单个种子用于观察，不足以断言算法优劣；完整实验应重复独立训练。`;
      }else if(kind==='bellman'){
        let values=[0,0,0,0];for(let k=0;k<v;k++){values=values.map((_,i)=>i===3?1:.9*values[i+1]);}
        svg.innerHTML=values.map((x,i)=>{const a=30+i*163;return `<rect x="${a}" y="85" width="125" height="85" rx="6" fill="var(--accent-soft)" stroke="var(--line)"/>`+text(a+62,112,`位置${i}`,'var(--text)','middle')+text(a+62,146,x.toFixed(3),'var(--accent)','middle')+(i<3?line(a+126,126,a+158,126,'var(--accent)',2):'');}).join('')+text(30,225,'最后一步才得1分；数值来自同步递推，不是预制动画。');result.textContent=`第${v}轮：V=[${values.map(x=>x.toFixed(3)).join(', ')}]。奖励信息每轮最多向前传播一个转移。`;
      }else if(kind==='ppo'){
        const eps=.2,r=v/.4,clip=x=>Math.max(1-eps,Math.min(1+eps,x));const points=Array.from({length:100},(_,i)=>.1+i*2.3/99);
        const axes=chart(svg,[{name:'A=+1: min(r, clip(r))',color:'var(--accent)',data:points.map(x=>[x,Math.min(x,clip(x))])},{name:'A=−1: min(−r, −clip(r))',color:'var(--warm)',data:points.map(x=>[x,Math.min(-x,-clip(x))])}],'新旧动作概率比 r','代理目标',[-2.5,1.5]);svg.innerHTML+=line(axes.px(r),43,axes.px(r),211,'var(--text)',1.5);result.textContent=`r=${r.toFixed(3)}；正优势目标=${Math.min(r,clip(r)).toFixed(3)}，负优势目标=${Math.min(-r,-clip(r)).toFixed(3)}。clip限制特定方向上的奖励增益，未强制所有概率比或KL满足硬约束。`;
      }else if(kind==='entropy'){
        const z=[0,1,2].map(q=>Math.exp((q-2)/v)),sum=z.reduce((a,b)=>a+b),p=z.map(x=>x/sum),h=-p.reduce((a,x)=>a+x*Math.log(x),0);
        svg.innerHTML=line(70,210,630,210)+p.map((x,i)=>`<rect x="${120+i*180}" y="${210-165*x}" width="90" height="${165*x}" fill="var(--accent)"/>`+text(165+i*180,238,`动作${i}`,'var(--text)','middle')+text(165+i*180,198-165*x,x.toFixed(3),'var(--text)','middle')).join('');result.textContent=`π=[${p.map(x=>x.toFixed(3)).join(', ')}]；熵H=${h.toFixed(3)} nats。温度提高使分布更均匀，离散最优分布由熵正则目标解析求得。`;
      }else if(kind==='model'){
        const truth=Array.from({length:26},(_,t)=>[t,1.02**t]),model=Array.from({length:26},(_,t)=>[t,(1.02+v)**t]);chart(svg,[{name:'真实系统',color:'var(--accent)',data:truth},{name:'有偏模型',color:'var(--warm)',data:model}],'预测步数','状态 x');result.textContent=`第25步绝对误差=${Math.abs(truth[25][1]-model[25][1]).toFixed(3)}。这是无控制的标量示例；闭环误差还受策略、稳定性和重规划影响。`;
      }
    }
    input.addEventListener('input',draw);draw();
  });
});
