// Sidebar toggle (mobile)
const menuBtn = document.getElementById('menuBtn');
if (menuBtn) menuBtn.addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));

// Toasts auto-dismiss
document.querySelectorAll('.toast').forEach((t, i) => {
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 400); }, 4500 + i * 600);
});

// Confirmation dialog for forms with data-confirm
const dlg = document.getElementById('confirmDlg');
document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', e => {
    if (form.dataset.confirmed) return;
    e.preventDefault();
    document.getElementById('dlgText').textContent = form.dataset.confirm;
    document.getElementById('dlgTitle').textContent = form.dataset.danger ? 'Cancel registration?' : 'Confirm registration';
    document.getElementById('dlgOk').textContent = form.dataset.danger ? 'Yes, cancel' : 'Register';
    dlg.returnValue = '';
    dlg.showModal();
    dlg.addEventListener('close', function once() {
      dlg.removeEventListener('close', once);
      if (dlg.returnValue === 'ok') { form.dataset.confirmed = '1'; form.submit(); }
    });
  });
});

// Animated stat counters
document.querySelectorAll('[data-count]').forEach(el => {
  const target = +el.dataset.count, start = performance.now(), dur = 600;
  const tick = now => {
    const p = Math.min((now - start) / dur, 1);
    el.textContent = Math.round(target * p);
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
});

// Countdown to next exam
const next = document.querySelector('.next[data-start]');
if (next) {
  const end = new Date(next.dataset.start).getTime();
  const set = (id, v) => document.getElementById(id).textContent = v;
  const update = () => {
    let s = Math.max(Math.floor((end - Date.now()) / 1000), 0);
    set('cd-d', Math.floor(s / 86400)); set('cd-h', Math.floor(s % 86400 / 3600));
    set('cd-m', Math.floor(s % 3600 / 60)); set('cd-s', s % 60);
  };
  update(); setInterval(update, 1000);
}

// Live search on exam list
const search = document.getElementById('liveSearch');
if (search) {
  search.addEventListener('input', () => {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    document.querySelectorAll('#examGrid .exam').forEach(c => {
      const hit = c.dataset.search.includes(q);
      c.classList.toggle('hidden', !hit);
      if (hit) shown++;
    });
    document.getElementById('noMatch').classList.toggle('hidden', shown > 0);
  });
  search.form.addEventListener('submit', e => e.preventDefault());
}
