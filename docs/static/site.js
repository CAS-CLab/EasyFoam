
document.querySelectorAll('[role="tab"]').forEach(tab => {
  tab.addEventListener('click', () => {
    const group = tab.closest('.code-panel');
    group.querySelectorAll('[role="tab"]').forEach(t => {
      t.setAttribute('aria-selected', String(t === tab));
      t.tabIndex = t === tab ? 0 : -1;
    });
    group.querySelectorAll('[role="tabpanel"]').forEach(p => p.hidden = p.id !== tab.getAttribute('aria-controls'));
  });
  tab.addEventListener('keydown', event => {
    if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...tab.closest('[role="tablist"]').querySelectorAll('[role="tab"]')];
    let index = tabs.indexOf(tab);
    index = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[index].click(); tabs[index].focus();
  });
});
document.querySelectorAll('.copy').forEach(button => button.addEventListener('click', async () => {
  const panel = button.closest('.code-panel');
  const code = [...panel.querySelectorAll('pre')].find(pre => !pre.hidden);
  const original = button.dataset.label;
  try {
    const field = document.createElement('textarea');
    field.value = code.innerText;
    field.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.append(field); field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } finally { field.remove(); }
    if (!copied) await navigator.clipboard.writeText(code.innerText);
    button.textContent = document.documentElement.dataset.copied;
  } catch {
    const range = document.createRange(); range.selectNodeContents(code);
    const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
    button.textContent = document.documentElement.dataset.copyfail;
  }
  setTimeout(() => button.textContent = original, 2400);
}));
