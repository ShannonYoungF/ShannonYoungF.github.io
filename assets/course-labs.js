/* Self-contained teaching experiments: no network, libraries, or background loops. */
(() => {
  "use strict";
  const zh = document.documentElement.lang.startsWith("zh");
  const words = (cn, en) => zh ? cn : en;
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const mix = (a, b, p) => a + (b - a) * p;
  const fmt = (n, digits = 2) => Number(n.toFixed(digits)).toString();
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const mean = (xs) => xs.reduce((a, b) => a + b, 0) / xs.length;
  const variance = (xs) => xs.reduce((a, x) => a + (x - mean(xs)) ** 2, 0) / (xs.length - 1);
  const line = (x1, y1, x2, y2, cls = "lab-axis") => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"/>`;
  const text = (x, y, value, anchor = "start", cls = "") => `<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${esc(value)}</text>`;
  const dot = (x, y, r = 5, cls = "lab-point") => `<circle cx="${x}" cy="${y}" r="${r}" class="${cls}"/>`;
  const diamond = (x, y, r = 7) => `<path d="M${x},${y-r}l${r},${r}l-${r},${r}l-${r},-${r}Z" class="lab-point"/>`;
  const path = (points, cls = "lab-series") => `<path d="${points.map(([x,y], i) => `${i ? "L" : "M"}${fmt(x)},${fmt(y)}`).join(" ")}" class="${cls}"/>`;
  const arrow = (x1, y, x2, cls) => line(x1,y,x2,y,cls) + (Math.abs(x2-x1) > 4 ? `<path d="M${x2},${y}l${x2>x1 ? -6 : 6},-4v8Z" class="lab-point"/>` : "");
  const axis = (x, y, ticks, label) => line(x(ticks[0]),y,x(ticks[ticks.length-1]),y) + ticks.map(t => line(x(t),y,x(t),y+4) + text(x(t),y+20,fmt(t),"middle","lab-label")).join("") + text(x(ticks[ticks.length-1]),y+40,label,"end","lab-label");
  const curve = (fn, x, y, low, high, cls) => path(Array.from({length:101}, (_,i) => { const t=mix(low,high,i/100); return [x(t),y(fn(t))]; }), cls);
  const gaussian = (x, m, s) => Math.exp(-.5*((x-m)/s)**2)/(s*Math.sqrt(2*Math.PI));
  const initialEnsemble = [.4,.8,1.2,1.6,2,2.4];
  const labs = [];

  // A fixed seed makes Q comparisons repeatable. Parameter and observation
  // perturbations use separate draws from the same pseudorandom stream.
  function normals(seed, count) {
    let state = seed >>> 0;
    const uniform = () => { state=(1664525*state+1013904223)>>>0; return (state+.5)/4294967296; };
    return Array.from({length:count}, () => Math.sqrt(-2*Math.log(uniform()))*Math.cos(2*Math.PI*uniform()));
  }
  function ekiRound(parameters, q, round) {
    const z = normals(1427+round*137, parameters.length*2);
    const perturbed = parameters.map((v,i) => v+q*z[i]);
    const predicted = perturbed.map(v => 2*v);
    const pm = mean(perturbed), hm = mean(predicted);
    const cross = perturbed.reduce((s,v,i) => s+(v-pm)*(predicted[i]-hm),0)/(parameters.length-1);
    const gain = cross/(variance(predicted)+1);
    const updated = perturbed.map((v,i) => v+gain*(6+z[i+parameters.length]-predicted[i]));
    return {before:[...parameters], perturbed, updated, gain};
  }

  class Experiment {
    constructor(el) {
      this.el=el;
      this.kind=el.dataset.lab;
      this.svg=el.querySelector("svg");
      this.result=el.querySelector(".lab-result");
      this.play=el.querySelector("[data-lab-play]");
      this.reset=el.querySelector("[data-lab-reset]");
      this.inputs=[...el.querySelectorAll("[data-key]")];
      this.defaults=this.inputs.map(input => input.value);
      this.progress=1;
      this.running=false;
      this.parameters=[...initialEnsemble];
      this.round=0;
      this.roundData=null;
      this.legend=document.createElement("div");
      this.legend.className="lab-legend";
      if (this.kind === "bayes") this.legend.innerHTML=`<span class="muted">${words("原先猜测","Original guess")}</span><span class="alt">${words("线索支持","Clue / likelihood")}</span><span>${words("更新后猜测","Updated guess")}</span>`;
      if (this.kind === "eki") {
        this.legend.className="lab-steps";
        this.legend.innerHTML=[words("① 探索","① Explore"),words("② 预测","② Predict"),words("③ 比较","③ Compare"),words("④ 更新","④ Update")].map(w=>`<span>${w}</span>`).join("");
      }
      el.querySelector(".lab-stage").before(this.legend);
      this.inputs.forEach(input => input.addEventListener("input", () => {
        this.stop(); this.progress=1;
        if (this.kind === "eki") this.clearEnsemble();
        this.render(); this.announce(); this.buttonLabel();
      }));
      this.play.addEventListener("click", () => this.running ? this.pause() : this.start());
      this.reset.addEventListener("click", () => {
        this.stop(); this.progress=1; this.clearEnsemble();
        this.inputs.forEach((input,i) => {input.value=this.defaults[i];});
        this.render(); this.announce(); this.buttonLabel();
      });
      el.classList.add("lab-ready");
      el.querySelectorAll(".lab-controls,.lab-actions").forEach(e => {e.hidden=false;});
      this.motionNote();
      new ResizeObserver(() => this.render()).observe(el.querySelector(".lab-stage"));
      this.render(); this.announce();
    }
    clearEnsemble() { this.parameters=[...initialEnsemble]; this.round=0; this.roundData=null; }
    motionNote() { this.el.querySelector(".lab-motion-note").textContent=motion.matches ? words("已减少动态效果：播放时直接展示结果","Reduced motion: play shows the result directly") : words("按播放才会动，随时可暂停","Play to animate; pause any time"); }
    values() { return Object.fromEntries(this.inputs.map(input=>[input.dataset.key,input.type === "range" ? Number(input.value) : input.value])); }
    buttonLabel() {
      this.play.textContent=this.running ? words("暂停","Pause") : this.progress<1 ? words("继续播放","Continue") : this.kind === "eki" ? words("播放一轮更新","Play one update") : words("播放小实验","Play experiment");
      this.play.setAttribute("aria-pressed",String(this.running));
    }
    stop() { cancelAnimationFrame(this.frame); this.running=false; }
    pause() { this.stop(); this.buttonLabel(); }
    start() {
      if (this.progress>=1) {
        this.progress=0;
        if (this.kind === "eki") this.roundData=ekiRound(this.parameters,this.values().explore,this.round);
      }
      if (motion.matches) { this.progress=1; this.complete(); return; }
      this.running=true; this.buttonLabel();
      const duration=this.kind === "eki" ? 6400 : 3600;
      const start=performance.now()-this.progress*duration;
      const tick=(now)=>{
        if (!this.running) return;
        this.progress=clamp((now-start)/duration);
        this.render();
        if (this.progress<1) this.frame=requestAnimationFrame(tick);
        else this.complete();
      };
      this.frame=requestAnimationFrame(tick);
    }
    complete() {
      this.stop();
      if (this.kind === "eki" && this.roundData) {this.parameters=[...this.roundData.updated]; this.round++;}
      this.render(); this.announce(); this.buttonLabel();
    }
    announce() { this.result.textContent=this.message; }
    render() {
      const v=this.values(), p=this.progress;
      this.inputs.forEach(input=>{
        const out=this.el.querySelector(`[data-value="${input.dataset.key}"]`);
        if(out) out.textContent=fmt(Number(input.value));
      });
      const W=Math.max(250,this.el.querySelector(".lab-stage").clientWidth);
      let H=250, s="";
      if (this.kind === "cars") {
        H=286;
        const x=n=>36+(W-66)*n/22, t=v.time*p;
        [.9,1,1.1].forEach((speed,i)=>{
          const y=46+i*70, pos=x(speed*t);
          s+=text(8,y-18,`${fmt(speed,1)} m/s`)+text(W-8,y-18,`${fmt(speed*t,1)} m`,"end");
          s+=line(x(0),y+11,x(22),y+11)+line(x(0),y+9,pos,y+9,"lab-trail");
          s+=`<g transform="translate(${pos},${y})"><path d="M-15,6V-5h7l5,-8h12l5,8h5V6Z" class="lab-point"/><circle cx="-9" cy="9" r="4" fill="var(--text)"/><circle cx="11" cy="9" r="4" fill="var(--text)"/></g>`;
        });
        s+=axis(x,228,[0,10,22],words("位置（米）","Position (m)"));
        this.message=words(`${v.time} 秒后：最慢 ${fmt(.9*v.time)} 米，最快 ${fmt(1.1*v.time)} 米，相差 ${fmt(.2*v.time)} 米。`,`After ${v.time} s: ${fmt(.9*v.time)}–${fmt(1.1*v.time)} m, a gap of ${fmt(.2*v.time)} m.`);
      }
      if (this.kind === "spread") {
        const x=n=>30+(W-60)*n/10, d=v.spread*p;
        s+=line(x(5),24,x(5),202,"lab-series-muted lab-dashed");
        [5-d,5,5+d].forEach(n=>{
          for(let j=0;j<5;j++) s+=dot(x(n),180-j*25,8);
          s+=text(x(n),38,fmt(n,1),"middle");
        });
        s+=axis(x,200,[0,5,10],words("每袋糖果数（颗）","Sweets per bag"));
        this.message=words(`三种可能：${5-v.spread}、5、${5+v.spread} 颗；平均仍是 5 颗，标准差 ${fmt(v.spread*Math.sqrt(2/3))} 颗。`,`Possible counts: ${5-v.spread}, 5, ${5+v.spread}. Mean stays 5; standard deviation ${fmt(v.spread*Math.sqrt(2/3))}.`);
      }
      if (this.kind === "correlation") {
        const cases=v.relation === "same" ? [[-1,-1],[1,1]] : v.relation === "opposite" ? [[-1,1],[1,-1]] : [[-1,-1],[-1,1],[1,-1],[1,1]];
        H=cases.length*67+70;
        const x=n=>32+(W-64)*(n+2)/4;
        cases.forEach(([a,b],i)=>{
          const y=38+i*67, p1=clamp(p*2), p2=clamp(p*2-1);
          s+=line(x(-2),y,x(2),y)+dot(x(0),y,3,"lab-point-alt");
          s+=arrow(x(0),y-7,x(a*p1),"lab-series-muted lab-dashed");
          s+=arrow(x(a*p1),y+7,x(a*p1+b*p2),"lab-series");
          s+=dot(x(a*p1+b*p2),y+7,5);
          s+=text(W/2,y+31,`${a>0?"+":""}${a} ${b>0?"+":"−"} ${Math.abs(b)} = ${a+b} m`,"middle");
        });
        s+=axis(x,H-52,[-2,0,2],words("相对起点的偏移（米）","Offset from start (m)"));
        const totalVar=v.relation === "same" ? 4 : v.relation === "opposite" ? 0 : 2;
        this.message=words(`每一步的标准差都是 1 米；两步合起来的标准差是 ${fmt(Math.sqrt(totalVar))} 米。${totalVar===0?"反向偏差恰好抵消了。":"它们的关系改变了总分散程度。"}`,`Each step has a standard deviation of 1 m; the total has ${fmt(Math.sqrt(totalVar))} m. ${totalVar===0?"Opposite errors cancel exactly.":"Their relationship changes the total spread."}`);
      }
      if (this.kind === "machine") {
        H=275;
        const x=n=>32+(W-64)*(n+4)/8;
        s+=text(8,20,words("输入：五种等可能数字","Input: five equally likely numbers"));
        s+=axis(x,52,[-4,0,4],"");
        s+=text(W/2,139,v.rule === "double" ? "× 2" : "× "+words("自己","itself"),"middle");
        s+=axis(x,210,[-4,0,4],words("输出数字","Output value"));
        [-2,-1,0,1,2].forEach((n,i)=>{
          const output=v.rule === "double" ? n*2 : n*n;
          const y2=210+(v.rule === "square" ? (i-2)*3 : 0);
          s+=line(x(n),52,x(output),y2,"lab-trail");
          s+=dot(x(n),52,4,"lab-point-alt")+dot(x(output),y2,4);
          s+=dot(mix(x(n),x(output),p),mix(52,y2,p),7);
        });
        this.message=v.rule === "square" ? words("输入平均是 0。先平方再平均得到 2；先平均再平方却得到 0。顺序会改变答案！","Input mean = 0. Average of squares = 2; square of the average = 0. The order matters!") : words("翻倍时：输入平均是 0，输出平均也是 0；珠子之间的距离变成两倍。","Doubling: input and output means are both 0; distances between beads double.");
      }
      if (this.kind === "bayes") {
        H=265;
        const r=v.noise**2, sd=Math.sqrt(1/(.25+1/r)), m=(1+v.reading/r)/(.25+1/r);
        const x=n=>34+(W-68)*(n+2)/14, maxDensity=1/(Math.min(sd,v.noise)*Math.sqrt(2*Math.PI))*1.16;
        const y=n=>207-175*n/maxDensity;
        s+=curve(n=>gaussian(n,4,2),x,y,-2,12,"lab-series-muted lab-dotted");
        s+=curve(n=>gaussian(n,v.reading,v.noise),x,y,-2,12,"lab-series-alt lab-dashed");
        s+=curve(n=>gaussian(n,mix(4,m,p),mix(2,sd,p)),x,y,-2,12,"lab-series");
        s+=axis(x,207,W<440 ? [0,6,12] : [0,4,8,12],words("可能的位置（米）","Possible position (m)"));
        s+=text(4,17,words("曲线高度：对位置的支持程度","Curve height: support for a location"),"start","lab-label");
        this.message=words(`原先中心 4 米 → 更新后中心 ${fmt(m)} 米；标准差从 2 米变为 ${fmt(sd)} 米。线索越模糊，原先猜测的分量越大。`,`Centre: 4 → ${fmt(m)} m. Standard deviation: 2 → ${fmt(sd)} m. A blurrier clue leaves more weight on the original guess.`);
      }
      if (this.kind === "noise") {
        H=275;
        const x=n=>28+(W-56)*n/10;
        s+=text(8,20,words("菱形：可能的位置","Diamonds: possible positions"));
        s+=text(8,153,words("圆点：下一次可能的读数","Circles: possible future readings"));
        [-1,1].forEach(a=>{
          const start=5+a*v.model;
          s+=diamond(x(start),60);
          [-1,1].forEach(b=>{
            const finish=start+b*v.noise;
            const endY=185+(a+b)*5;
            s+=line(x(start),60,x(finish),endY,"lab-trail");
            s+=dot(mix(x(start),x(finish),p),mix(60,endY,p),6);
          });
        });
        s+=axis(x,214,[0,5,10],words("位置 / 读数（米）","Position / reading (m)"));
        this.message=words(`位置方差 ${fmt(v.model**2)} + 测量噪声方差 ${fmt(v.noise**2)} = 读数方差 ${fmt(v.model**2+v.noise**2)}（平方米）。尺子稳了，位置的未知仍可能存在。`,`Position variance ${fmt(v.model**2)} + noise variance ${fmt(v.noise**2)} = reading variance ${fmt(v.model**2+v.noise**2)} m². A steady ruler can still leave uncertainty about position.`);
      }
      if (this.kind === "operator") {
        H=496;
        const x=t=>42+(W-65)*t/4, time=v.query*p;
        const flow=t=>v.shape === "steady" ? 2 : v.shape === "rising" ? t/2 : 2*(1+.6*Math.sin(Math.PI*t/2));
        const volume=t=>v.shape === "steady" ? 2*t : v.shape === "rising" ? t*t/4 : 2*(t+1.2/Math.PI*(1-Math.cos(Math.PI*t/2)));
        const bucket=W-55, waterHeight=volume(time)*6;
        s+=text(8,49,words(`第 ${fmt(time,1)} 秒`,`${fmt(time,1)} seconds`));
        s+=text(8,76,words(`积水 ${fmt(volume(time))} 升`,`${fmt(volume(time))} L collected`));
        s+=line(bucket-65,15,bucket,15,"lab-series-muted")+line(bucket,15,bucket,30,"lab-series-muted");
        s+=`<rect x="${bucket-31}" y="${108-waterHeight}" width="62" height="${waterHeight}" class="lab-fill"/>`;
        s+=`<path d="M${bucket-36},43v67h72V43" class="lab-series"/>`;
        s+=line(bucket,33,bucket,Math.max(44,108-waterHeight),"lab-series lab-dashed");
        const panels=[{top:158,bottom:265,max:4,fn:flow,label:words("进水速度（升/秒）","Flow rate (L/s)")},{top:339,bottom:446,max:10,fn:volume,label:words("已经积的水（升）","Water collected (L)")}];
        panels.forEach(({top,bottom,max,fn,label})=>{
          const y=n=>bottom-(bottom-top)*n/max;
          s+=text(4,top-10,label)+line(x(0),top,x(0),bottom);
          [0,max].forEach(n=>{s+=text(32,y(n)+4,n,"end","lab-label");});
          const fillPoints=[[x(0),bottom],...Array.from({length:61},(_,i)=>[x(time*i/60),y(fn(time*i/60))]),[x(time),bottom]];
          s+=`<path d="${fillPoints.map(([a,b],i)=>`${i?"L":"M"}${a},${b}`).join(" ")}Z" class="lab-fill"/>`;
          s+=curve(fn,x,y,0,4,"lab-series")+line(x(time),top,x(time),bottom,"lab-series-muted lab-dashed")+dot(x(time),y(fn(time)),6);
          s+=axis(x,bottom,W<440?[0,2,4]:[0,1,2,3,4],words("时间（秒）","Time (s)"));
        });
        this.message=words(`Trunk 询问第 ${fmt(v.query,1)} 秒 → 水量 ${fmt(volume(v.query))} 升。Branch 需要读取整条进水曲线；改变开水方式，整条积水曲线也会改变。`,`Trunk queries ${fmt(v.query,1)} s → ${fmt(volume(v.query))} L collected. Branch reads the whole input curve; changing the tap pattern changes the entire output curve.`);
      }
      if (this.kind === "kalman") {
        H=290;
        const r=v.noise**2, k=4/(4+r), m=4+k*4, sd=Math.sqrt((1-k)*4), x=n=>28+(W-56)*(n+1)/14;
        const rows=[{y:52,m:4,sd:2,label:words("原先估计","Original"),cls:"lab-series-muted"},{y:125,m:8,sd:v.noise,label:words("传感器","Sensor"),cls:"lab-series-alt"},{y:200,m:mix(4,m,p),sd:mix(2,sd,p),label:words("更新后","Updated"),cls:"lab-series"}];
        rows.forEach((row,i)=>{
          s+=text(8,row.y-19,row.label)+line(x(row.m-row.sd),row.y,x(row.m+row.sd),row.y,row.cls);
          s+=line(x(row.m-row.sd),row.y-5,x(row.m-row.sd),row.y+5,row.cls)+line(x(row.m+row.sd),row.y-5,x(row.m+row.sd),row.y+5,row.cls);
          s+=dot(x(row.m),row.y,6,i===1?"lab-point-alt":"lab-point")+text(W-8,row.y-19,`${fmt(row.m)} m`,"end");
        });
        s+=axis(x,234,[0,4,8,12],words("位置（米）","Position (m)"));
        this.message=words(`传感器权重 K=${fmt(k)}；新位置 ${fmt(m)} 米。传感器越准，结果越靠近 8 米；越模糊，越靠近原先的 4 米。`,`Sensor weight K=${fmt(k)}; updated position ${fmt(m)} m. A more precise sensor pulls harder toward 8 m; a less precise one leaves the estimate nearer 4 m.`);
      }
      if (this.kind === "eki") {
        H=275;
        const data=this.roundData;
        let parameters=this.parameters;
        if(data) parameters=data.before.map((v,i)=>mix(mix(v,data.perturbed[i],clamp(p*4)),data.updated[i],clamp(p*4-3)));
        const all=[0,3, ...parameters, ...(data?data.before:[])];
        const low=Math.min(-.5,Math.min(...all)-.3), high=Math.max(5,Math.max(...all)+.3);
        const x=n=>28+(W-56)*(n-low)/(high-low);
        s+=text(8,21,words("参数猜测 θ","Parameter guesses θ"))+text(8,160,words("模型预测：2 × θ","Model prediction: 2 × θ"));
        s+=line(x(low),62,x(high),62)+line(x(low),199,x(high),199);
        s+=line(x(3),166,x(3),225,"lab-series-alt lab-dashed")+text(x(3),244,words("观测 = 6","Observed = 6"),"middle");
        parameters.forEach((param,i)=>{
          const jitter=(i-2.5)*6;
          s+=dot(x(param),62+jitter,6);
          const travel=data ? clamp(p*4-1) : 1;
          s+=line(x(param),62+jitter,x(param),199+jitter,"lab-trail");
          s+=dot(x(param),mix(62+jitter,199+jitter,travel),5);
          if(data && p>.5 && p<.75) s+=arrow(x(param),199+jitter,x(3),"lab-series-muted lab-dashed");
        });
        s+=text(x(low),88,fmt(low,1))+text(x(high),88,fmt(high,1),"end");
        [...this.legend.children].forEach((span,i)=>span.classList.toggle("is-current",Boolean(data)&&i===Math.min(3,Math.floor(p*4))));
        const outputs=parameters.map(a=>2*a);
        this.message=words(`已完成 ${this.round} 轮；预测均值 ${fmt(mean(outputs))}，观测为 6；成员预测的样本标准差 ${fmt(Math.sqrt(variance(outputs)))}。这是小模型的演示，不代表误差或精确后验。`,`${this.round} rounds completed. Prediction mean ${fmt(mean(outputs))}; observation 6; sample standard deviation ${fmt(Math.sqrt(variance(outputs)))}. Ensemble spread is not error or proof of an exact posterior.`);
      }
      if (this.kind === "coverage") {
        H=275;
        const errors=[-2,-1.6,-1.2,-.8,-.4,-.1,.2,.5,.9,1.3,1.7,2.2], x=i=>40+(W-64)*i/11, y=n=>130-33*n;
        s+=`<rect x="34" y="${y(v.width)}" width="${W-52}" height="${66*v.width}" class="lab-fill"/>`;
        s+=line(34,y(0),W-18,y(0),"lab-series lab-dashed");
        [-3,0,3].forEach(n=>{s+=text(25,y(n)+4,n,"end","lab-label");});
        let count=0;
        errors.forEach((e,i)=>{
          const inside=Math.abs(e)<=v.width+1e-9, yp=mix(18,y(e),clamp(p*1.5-i/24));
          if(inside) { count++; s+=dot(x(i),yp,5); }
          else s+=path([[x(i)-4,yp-4],[x(i)+4,yp+4]],"lab-series-alt")+path([[x(i)-4,yp+4],[x(i)+4,yp-4]],"lab-series-alt");
        });
        s+=text(4,15,words("真实误差（米）","True error (m)"))+text(W-18,258,words("12 回不同预测 →","12 different predictions →"),"end","lab-label");
        this.message=words(`接住 ${count} / 12 个点，覆盖率 ${fmt(count/12*100,1)}%；范围总宽 ${fmt(2*v.width)} 米。范围变宽，通常更容易接住点，但也更不精细。`,`${count} / 12 points inside: ${fmt(count/12*100,1)}% coverage. Total band width ${fmt(2*v.width)} m. A wider band catches more points but is less specific.`);
      }
      this.svg.setAttribute("viewBox",`0 0 ${W} ${H}`);
      this.svg.style.height=`${H}px`;
      this.svg.innerHTML=`<title>${esc(this.el.querySelector("h3").textContent)}</title><desc>${esc(this.message)}</desc>${s}`;
    }
  }
  document.querySelectorAll(".intuition-lab").forEach(el=>labs.push(new Experiment(el)));
  const visible=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(!entry.isIntersecting) labs.find(lab=>lab.el===entry.target)?.pause();
  }));
  labs.forEach(lab=>visible.observe(lab.el));
  document.addEventListener("visibilitychange",()=>{if(document.hidden) labs.forEach(lab=>lab.pause());});
  motion.addEventListener("change",()=>labs.forEach(lab=>{ if(motion.matches) lab.pause(); lab.motionNote(); }));
})();
