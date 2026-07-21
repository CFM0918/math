document.addEventListener('DOMContentLoaded',()=>{
  const tabs=[...document.querySelectorAll('.tab')],panels=[...document.querySelectorAll('.panel')];
  tabs.forEach((tab,i)=>tab.addEventListener('click',()=>{tabs.forEach(x=>x.classList.remove('on'));panels.forEach(x=>x.classList.remove('on'));tab.classList.add('on');panels[i]?.classList.add('on');window.scrollTo({top:document.querySelector('.tabs')?.offsetTop-70||0,behavior:'smooth'});}));
  const questions=[...document.querySelectorAll('.question')];let answered=0,correct=0;
  questions.forEach(q=>q.querySelectorAll('.choice').forEach(btn=>btn.addEventListener('click',()=>{
    if(q.dataset.done)return;q.dataset.done='1';answered++;
    const ok=btn.dataset.correct==='true';if(ok)correct++;
    q.querySelectorAll('.choice').forEach(x=>{x.disabled=true;if(x.dataset.correct==='true')x.classList.add('correct')});
    if(!ok)btn.classList.add('wrong');const fb=q.querySelector('.feedback');if(fb){fb.classList.add('on');fb.textContent=(ok?'答對了！':'再看一次：')+(q.dataset.explain||'請依公式逐步檢查。')}
    const total=questions.length;document.querySelectorAll('[data-score]').forEach(x=>x.textContent=correct);document.querySelectorAll('[data-answered]').forEach(x=>x.textContent=answered);document.querySelectorAll('[data-total]').forEach(x=>x.textContent=total);document.querySelectorAll('.progress span').forEach(x=>x.style.width=`${answered/total*100}%`);
  })));
  document.querySelectorAll('[data-reset]').forEach(btn=>btn.addEventListener('click',()=>location.reload()));
  const slides=[...document.querySelectorAll('.slide')];let current=0;
  const focus=n=>{if(!slides.length)return;current=(n+slides.length)%slides.length;slides.forEach(x=>x.classList.remove('focus'));slides[current].classList.add('focus');slides[current].scrollIntoView({behavior:'smooth',block:'center'});};
  document.querySelector('[data-prev]')?.addEventListener('click',()=>focus(current-1));document.querySelector('[data-next]')?.addEventListener('click',()=>focus(current+1));
  if(slides.length){slides.forEach((s,i)=>s.addEventListener('click',()=>current=i));document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();focus(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();focus(current-1)}})}
});
