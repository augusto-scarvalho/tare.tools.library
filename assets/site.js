---
---
(() => {
  const menuButton = document.querySelector('.menu-button');
  const sidebar = document.getElementById('sidebar');
  if (menuButton && sidebar) {
    menuButton.addEventListener('click', () => {
      const open = sidebar.classList.toggle('is-open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
  }

  const input = document.getElementById('site-search');
  const results = document.getElementById('search-results');
  if (!input || !results) return;

  let index = [];
  fetch('{{ "/search.json" | relative_url }}')
    .then(r => r.ok ? r.json() : Promise.reject(new Error('search index unavailable')))
    .then(data => { index = [...(data.pages || []), ...(data.studies || [])]; })
    .catch(() => { index = []; });

  const close = () => { results.hidden = true; results.innerHTML = ''; };
  const render = (query) => {
    const q = query.trim().toLowerCase();
    if (q.length < 2) return close();
    const hits = index
      .map(item => ({ item, score: ((item.title || '').toLowerCase().includes(q) ? 4 : 0) + ((item.text || '').toLowerCase().includes(q) ? 1 : 0) }))
      .filter(x => x.score > 0)
      .sort((a,b) => b.score - a.score)
      .slice(0, 12);
    results.innerHTML = '';
    if (!hits.length) {
      results.innerHTML = '<div class="search-item">No matching research found.</div>';
      results.hidden = false;
      return;
    }
    for (const {item} of hits) {
      const a = document.createElement('a');
      a.className = 'search-item';
      a.href = item.url;
      const title = document.createElement('strong');
      title.textContent = item.title || item.url;
      const meta = document.createElement('small');
      meta.textContent = item.kind === 'study' ? 'Rendered HTML study edition' : (item.path || 'Research page');
      a.append(title, meta);
      results.appendChild(a);
    }
    results.hidden = false;
  };

  input.addEventListener('input', () => render(input.value));
  input.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  document.addEventListener('click', e => { if (!results.contains(e.target) && e.target !== input) close(); });
})();
