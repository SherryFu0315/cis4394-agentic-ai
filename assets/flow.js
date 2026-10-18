/* flow.js — dependency-free animated flow diagrams for CIS 4394.
   Usage: Flow.mount(element, spec)
   spec = { w, h, title, intro, nodes:[{id,x,y,w,h,label,sub,kind}], edges:[{from,to,curve,label,both}],
            counters:[{key,label,fmt}], start:'key', scenarios:{ key:{ name, steps:[ step… ] } } }
   step = { move:[from,to], packet:'label', at:'nodeId', tone:'info|ok|warn|bad', say:'html', payload:'text',
            set:{counterKey:+n}, mark:{nodeId:'blocked|ok|off'}, choice:[{label,goto,tone}], end:true, dur:ms }   */
(function(){
  var KIND={user:'#8ab4ff',model:'#7aa2ff',harness:'#b39dff',tool:'#5ad8a6',store:'#f2c94c',gate:'#ffb15e',ext:'#ff7a7a',doc:'#9fb3c8',agent:'#7aa2ff',out:'#9be7ff'};
  var TONE={info:'#7aa2ff',ok:'#5ad8a6',warn:'#ffb15e',bad:'#ff6b6b'};
  var NS='http://www.w3.org/2000/svg', seq=0;
  function el(tag,attrs,parent){var e=document.createElementNS(NS,tag);for(var k in attrs)e.setAttribute(k,attrs[k]);if(parent)parent.appendChild(e);return e;}
  function h(tag,cls,parent,text){var e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;if(parent)parent.appendChild(e);return e;}
  function esc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
  function border(n,tx,ty){var cx=n.x+n.w/2,cy=n.y+n.h/2,dx=tx-cx,dy=ty-cy;if(!dx&&!dy)return [cx,cy];
    var sx=(n.w/2)/Math.abs(dx||1e-9),sy=(n.h/2)/Math.abs(dy||1e-9),s=Math.min(sx,sy);return [cx+dx*s,cy+dy*s];}
  function fmt(c,v){if(c.fmt==='usd')return '$'+v.toFixed(v<1?3:2);if(c.fmt==='sec')return v.toFixed(1)+' s';return String(Math.round(v));}

  function mount(root,spec){
    var uid='fl'+(++seq), W=spec.w||760, H=spec.h||340;
    root.classList.add('flow'); root.innerHTML='';
    var stage=h('div','flow-stage',root);
    var svg=el('svg',{viewBox:'0 0 '+W+' '+H,'class':'flow-svg',role:'img','aria-label':spec.title||'animated flow diagram'},stage);
    var defs=el('defs',{},svg);
    var mk=el('marker',{id:uid+'-arr',viewBox:'0 0 10 10',refX:'9',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto'},defs);
    el('path',{d:'M0 0L10 5L0 10z',fill:'#56688a'},mk);
    var mk2=el('marker',{id:uid+'-arr2',viewBox:'0 0 10 10',refX:'9',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto'},defs);
    el('path',{d:'M0 0L10 5L0 10z',fill:'#7aa2ff'},mk2);
    var f=el('filter',{id:uid+'-glow',x:'-80%',y:'-80%',width:'260%',height:'260%'},defs);
    el('feGaussianBlur',{stdDeviation:'3.5',result:'b'},f); var m=el('feMerge',{},f); el('feMergeNode',{'in':'b'},m); el('feMergeNode',{'in':'SourceGraphic'},m);
    var gEdges=el('g',{'class':'flow-edges'},svg), gNodes=el('g',{'class':'flow-nodes'},svg), gPk=el('g',{'class':'flow-packets'},svg);

    var nodes={};
    spec.nodes.forEach(function(n){
      nodes[n.id]=n;
      var g=el('g',{'class':'flow-node kind-'+(n.kind||'doc'),'data-id':n.id,transform:'translate('+n.x+','+n.y+')'},gNodes);
      el('rect',{width:n.w,height:n.h,rx:10,ry:10,fill:n.kind==='ext'?'#2a1420':'#121c33',stroke:KIND[n.kind]||KIND.doc,'stroke-width':1.5},g);
      var t=el('text',{x:n.w/2,y:n.sub?n.h/2-3:n.h/2+5,'text-anchor':'middle','class':'flow-label'},g); t.textContent=n.label;
      if(n.sub){var s=el('text',{x:n.w/2,y:n.h/2+14,'text-anchor':'middle','class':'flow-sub'},g); s.textContent=n.sub;}
      if(n.badge){var b=el('text',{x:n.w-6,y:12,'text-anchor':'end','class':'flow-badge'},g); b.textContent=n.badge;}
      n._g=g;
    });
    var edges={};
    (spec.edges||[]).forEach(function(e){
      var a=nodes[e.from],b=nodes[e.to],d;
      if(e.d){d=e.d;}
      else{
        var p1=border(a,b.x+b.w/2,b.y+b.h/2),p2=border(b,a.x+a.w/2,a.y+a.h/2);
        if(e.curve){var mx=(p1[0]+p2[0])/2,my=(p1[1]+p2[1])/2,nx=-(p2[1]-p1[1]),ny=(p2[0]-p1[0]),L=Math.hypot(nx,ny)||1,k=e.curve/L;
          d='M'+p1[0]+' '+p1[1]+' Q'+(mx+nx*k)+' '+(my+ny*k)+' '+p2[0]+' '+p2[1];}
        else d='M'+p1[0]+' '+p1[1]+' L'+p2[0]+' '+p2[1];
      }
      var p=el('path',{d:d,'class':'flow-edge',fill:'none','marker-end':'url(#'+uid+'-arr)'},gEdges);
      if(e.label){var L2=p.getTotalLength(),pt=p.getPointAtLength(L2/2);var tl=el('text',{x:pt.x,y:pt.y-6,'text-anchor':'middle','class':'flow-edge-label'},gEdges);tl.textContent=e.label;}
      edges[e.from+'>'+e.to]=p; if(e.both)edges[e.to+'>'+e.from]=p;
    });

    var panel=h('div','flow-panel',root);
    var ctl=h('div','flow-ctl',panel), tabs=h('div','flow-tabs',ctl);
    var btnBack=h('button','flow-btn',ctl,'◀'), btnPlay=h('button','flow-btn primary',ctl,'▶ Play'), btnStep=h('button','flow-btn',ctl,'Step ▶'), btnReset=h('button','flow-btn',ctl,'↺ Reset');
    btnBack.title='Back one step (←)'; btnStep.title='Forward one step (→)'; btnPlay.title='Play / pause (space)';
    var speed=h('select','flow-speed',ctl); ['0.5','1','2'].forEach(function(v){var o=h('option','',speed,v+'×');o.value=v;if(v==='1')o.selected=true;});
    var prog=h('span','flow-prog',ctl,'');
    var say=h('div','flow-say',panel,''), pay=h('pre','flow-pay',panel,''), counters=h('div','flow-counters',panel), choices=h('div','flow-choices',panel);

    var keys=Object.keys(spec.scenarios), scen=spec.start||keys[0], i=0, playing=false, timer=null, anim=null, cnt={};
    function steps(){return spec.scenarios[scen].steps;}
    function spd(){return parseFloat(speed.value)||1;}
    function renderCounters(){counters.innerHTML='';(spec.counters||[]).forEach(function(c){var chip=h('span','flow-chip',counters);chip.innerHTML='<b>'+esc(fmt(c,cnt[c.key]||0))+'</b> '+esc(c.label);});}
    function clearActive(){var a=gNodes.querySelectorAll('.active');for(var k=0;k<a.length;k++)a[k].classList.remove('active');}
    function activate(id,tone){clearActive();var n=nodes[id];if(n&&n._g){n._g.classList.add('active');n._g.classList.add('on');n._g.style.setProperty('--tone',TONE[tone||'info']);}}
    function edgeFor(st){var p=edges[st.move[0]+'>'+st.move[1]],rev=false;if(!p&&edges[st.move[1]+'>'+st.move[0]]){p=edges[st.move[1]+'>'+st.move[0]];rev=true;}
      if(!p){var a=nodes[st.move[0]],b=nodes[st.move[1]],p1=border(a,b.x+b.w/2,b.y+b.h/2),p2=border(b,a.x+a.w/2,a.y+a.h/2);
        p=el('path',{d:'M'+p1[0]+' '+p1[1]+' L'+p2[0]+' '+p2[1],'class':'flow-edge temp',fill:'none','stroke-dasharray':'4 4'},gEdges);edges[st.move[0]+'>'+st.move[1]]=p;}
      return {p:p,rev:rev};}
    function showStep(st){
      if(st.say!=null)say.innerHTML=st.say;
      if(st.payload!=null){pay.textContent=st.payload;pay.style.display='block';}else if(st.clear){pay.style.display='none';}
      if(st.set){for(var k in st.set)cnt[k]=(cnt[k]||0)+st.set[k];renderCounters();}
      if(st.mark){for(var id in st.mark){var g=nodes[id]&&nodes[id]._g;if(!g)continue;if(st.mark[id]==='off')g.removeAttribute('data-state');else g.setAttribute('data-state',st.mark[id]);}}
      panel.setAttribute('data-tone',st.tone||'info');
      choices.innerHTML='';
      if(st.at)activate(st.at,st.tone);
      if(st.choice){st.choice.forEach(function(c){var b=h('button','flow-choice tone-'+(c.tone||'info'),choices,c.label);b.onclick=function(){go(c.goto);};});}
      panel.classList.toggle('ended',!!st.end);
    }
    function animateMove(st,done){
      var ef=edgeFor(st),p=ef.p,rev=ef.rev; p.classList.add('used'); p.setAttribute('marker-end','url(#'+uid+'-arr2)');
      var L=p.getTotalLength(),tone=TONE[st.tone||'info'];
      var g=el('g',{'class':'flow-packet'},gPk);
      el('circle',{r:7,fill:tone,filter:'url(#'+uid+'-glow)'},g);
      if(st.packet){var chip=el('g',{},g);var txt=el('text',{x:0,y:-15,'text-anchor':'middle','class':'flow-chip-t'},chip);txt.textContent=st.packet;
        var bb=txt.getBBox();var r=el('rect',{x:bb.x-7,y:bb.y-3,width:bb.width+14,height:bb.height+6,rx:7,fill:'#0b1324',stroke:tone,'stroke-width':1});chip.insertBefore(r,txt);}
      var dur=(st.dur||950)/spd(),t0=performance.now();
      activate(st.move[0],st.tone);
      function frame(now){var k=Math.min(1,(now-t0)/dur),e=k<.5?2*k*k:-1+(4-2*k)*k,pt=p.getPointAtLength((rev?1-e:e)*L);
        g.setAttribute('transform','translate('+pt.x+','+pt.y+')');
        if(k<1)anim=requestAnimationFrame(frame);else{g.remove();activate(st.move[1],st.tone);done();}}
      anim=requestAnimationFrame(frame);
    }
    function runStep(idx,instant,cb){var st=steps()[idx];if(!st){if(cb)cb();return;}
      showStep(st); prog.textContent=(idx+1)+' / '+steps().length;
      if(st.move&&!instant){animateMove(st,function(){if(cb)cb();});}
      else{if(st.move){var ef=edgeFor(st);ef.p.classList.add('used');ef.p.setAttribute('marker-end','url(#'+uid+'-arr2)');activate(st.move[1],st.tone);}if(cb)cb();}}
    function stop(){playing=false;btnPlay.textContent='▶ Play';clearTimeout(timer);}
    function next(){if(i>=steps().length){stop();return;}var st=steps()[i];i++;
      runStep(i-1,false,function(){if(playing){if(st.choice||st.end||i>=steps().length)stop();else timer=setTimeout(next,480/spd());}});}
    function play(){if(i>=steps().length)reset(false);playing=true;btnPlay.textContent='⏸ Pause';next();}
    function reset(full){stop();cancelAnimationFrame(anim);gPk.innerHTML='';
      var u=gEdges.querySelectorAll('.used');for(var k=0;k<u.length;k++){u[k].classList.remove('used');u[k].setAttribute('marker-end','url(#'+uid+'-arr)');}
      var t=gEdges.querySelectorAll('.temp');for(k=0;k<t.length;k++)t[k].remove();
      for(var key in edges)if(edges[key].classList.contains('temp'))delete edges[key];
      var on=gNodes.querySelectorAll('.on,.active');for(k=0;k<on.length;k++){on[k].classList.remove('on');on[k].classList.remove('active');}
      var ds=gNodes.querySelectorAll('[data-state]');for(k=0;k<ds.length;k++)ds[k].removeAttribute('data-state');
      i=0;if(full!==false)cnt={};renderCounters();
      say.innerHTML=spec.scenarios[scen].intro||spec.intro||'Press Play, or step through one event at a time.';
      pay.style.display='none';choices.innerHTML='';panel.classList.remove('ended');panel.setAttribute('data-tone','info');
      prog.textContent='0 / '+steps().length;}
    function back(){stop();cancelAnimationFrame(anim);var target=Math.max(0,i-1);reset(true);for(var k=0;k<target;k++)runStep(k,true);i=target;}
    function go(key){if(!spec.scenarios[key])return;stop();cancelAnimationFrame(anim);scen=key;var saved={};for(var k in cnt)saved[k]=cnt[k];reset(true);cnt=saved;renderCounters();
      var tb=tabs.querySelectorAll('button');for(var j=0;j<tb.length;j++)tb[j].classList.toggle('active',tb[j].getAttribute('data-k')===key);play();}
    var visible=keys.filter(function(k){return !spec.scenarios[k].hidden;});
    if(visible.length>1){visible.forEach(function(k){var b=h('button','flow-tab'+(k===scen?' active':''),tabs,spec.scenarios[k].name);b.setAttribute('data-k',k);
      b.onclick=function(){stop();cancelAnimationFrame(anim);scen=k;reset(true);var tb=tabs.querySelectorAll('button');for(var j=0;j<tb.length;j++)tb[j].classList.toggle('active',tb[j]===b);};});}
    btnPlay.onclick=function(){playing?stop():play();}; btnStep.onclick=function(){stop();if(i<steps().length)next();}; btnBack.onclick=back; btnReset.onclick=function(){reset(true);};
    root.tabIndex=0;
    root.addEventListener('keydown',function(e){if(e.key===' '){e.preventDefault();playing?stop():play();}else if(e.key==='ArrowRight'){e.preventDefault();stop();if(i<steps().length)next();}else if(e.key==='ArrowLeft'){e.preventDefault();back();}});
    reset(true);
    return {play:play,stop:stop,reset:reset,go:go};
  }
  window.Flow={mount:mount};
})();
