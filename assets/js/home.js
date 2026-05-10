document.addEventListener('DOMContentLoaded', () => {
  const dataEl = document.getElementById('home-data');
  const table = document.querySelector('[data-vocab-table]');
  const detail = document.querySelector('[data-detail]');
  const search = document.getElementById('vocab-search');
  const visibleCount = document.getElementById('visible-count');
  const totalCount = document.getElementById('total-count');
  const emptyState = document.getElementById('table-empty');
  const fullListUrl = detail?.dataset.fullListUrl || '#';

  if (!dataEl || !table || !detail) {
    return;
  }

  const data = JSON.parse(dataEl.textContent);
  const rows = Array.from(table.querySelectorAll('tbody tr[data-index]'));
  const rowData = data.rows || [];
  let activeIndex = 0;

  const esc = (value) => String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  const speaker = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 7 7.5 10H5v4h2.5L11 17V7z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"></path><path d="M14.5 9.5a3.8 3.8 0 0 1 0 5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"></path><path d="M16.8 7.2a7 7 0 0 1 0 9.6" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"></path></svg>';

  const renderDetail = (entry) => {
    if (!entry) {
      return;
    }

    detail.innerHTML = `
      <div class="detail-head">
        <div>
          <div class="detail-wordline">
            <h2>${esc(entry.word)}</h2>
            <span class="detail-speaker" aria-hidden="true">${speaker}</span>
          </div>
          <div class="detail-phonetic">UK <span>${esc(entry.uk)}</span></div>
          <div class="detail-phonetic">US <span>${esc(entry.us)}</span></div>
        </div>
        <div class="detail-meta">
          <span>${esc(entry.detail)}</span>
          <ul class="tag-list">${(entry.tags || []).map((tag) => `<li>${esc(tag)}</li>`).join('')}</ul>
        </div>
      </div>
      <section class="detail-examples">
        <h3>例句 <small>(${(entry.examples || []).length})</small></h3>
        <ol class="example-list">
          ${(entry.examples || []).map((example) => `
            <li>
              <div class="example-en">${esc(example.en)} <span class="example-speaker" aria-hidden="true">${speaker}</span></div>
              <div class="example-zh">${esc(example.zh)}</div>
            </li>
          `).join('')}
        </ol>
      </section>
      <a class="action-button detail-action" href="${esc(fullListUrl)}">查看完整词表</a>
    `;
  };

  const setActive = (index) => {
    activeIndex = index;
    rows.forEach((row) => row.classList.toggle('is-active', Number(row.dataset.index) === index));
    renderDetail(rowData[index]);
  };

  const updateCounts = () => {
    const visible = rows.filter((row) => !row.hidden).length;
    if (visibleCount) {
      visibleCount.textContent = String(visible);
    }
    if (totalCount) {
      totalCount.textContent = String(rows.length);
    }
    if (emptyState) {
      emptyState.hidden = visible !== 0;
    }
  };

  rows.forEach((row) => {
    const index = Number(row.dataset.index);
    row.addEventListener('click', () => setActive(index));
    row.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setActive(index);
      }
    });
  });

  search?.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    let firstVisible = -1;

    rows.forEach((row, index) => {
      const text = row.textContent.toLowerCase();
      const match = !query || text.includes(query);
      row.hidden = !match;
      if (match && firstVisible === -1) {
        firstVisible = index;
      }
    });

    updateCounts();
    if (firstVisible !== -1) {
      setActive(firstVisible);
    }
  });

  updateCounts();
  setActive(activeIndex);
});
