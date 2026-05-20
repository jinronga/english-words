document.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  const body = document.body;
  const pageKind = body?.dataset.pageKind || 'doc';
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const mediaQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  const storagePrefix = 'english-words:study:';

  const normalize = (value) => String(value ?? '').replace(/\s+/g, ' ').trim();

  const escapeHtml = (value) => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  const stripMd = (value) => normalize(value).replace(/\.md$/i, '');

  const safeGet = (key) => {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  };

  const safeSet = (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      // Storage can be blocked; the UI should still work.
    }
  };

  const safeKeys = () => {
    try {
      return Array.from({ length: localStorage.length }, (_, index) => localStorage.key(index)).filter(Boolean);
    } catch (error) {
      return [];
    }
  };

  const parseJson = (value) => {
    try {
      return JSON.parse(value);
    } catch (error) {
      return null;
    }
  };

  const addHash = (href, hash) => {
    if (!href) {
      return `#${hash}`;
    }

    try {
      const url = new URL(href, window.location.href);
      url.hash = hash;
      return url.toString();
    } catch (error) {
      return `${href.split('#')[0]}#${hash}`;
    }
  };

  const updateThemeButton = () => {
    if (!themeToggle) {
      return;
    }

    const theme = root.dataset.theme === 'dark' ? 'dark' : 'light';
    const nextTheme = theme === 'dark' ? '白色' : '暗黑';
    themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    themeToggle.setAttribute('aria-label', `切换到${nextTheme}模式`);
    themeToggle.title = `切换到${nextTheme}模式`;
  };

  const applyTheme = (theme, persist = false) => {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;

    if (persist) {
      safeSet('theme', theme);
    }

    updateThemeButton();
  };

  const storedTheme = safeGet('theme');
  const systemTheme = mediaQuery?.matches ? 'dark' : 'light';
  const initialTheme = root.dataset.theme === 'dark' || root.dataset.theme === 'light'
    ? root.dataset.theme
    : storedTheme === 'dark' || storedTheme === 'light'
      ? storedTheme
      : systemTheme;

  applyTheme(initialTheme);

  themeToggle?.addEventListener('click', () => {
    const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme, true);
  });

  const onSystemThemeChange = (event) => {
    const currentStoredTheme = safeGet('theme');
    if (!currentStoredTheme) {
      applyTheme(event.matches ? 'dark' : 'light');
    }
  };

  if (mediaQuery?.addEventListener) {
    mediaQuery.addEventListener('change', onSystemThemeChange);
  } else if (mediaQuery?.addListener) {
    mediaQuery.addListener(onSystemThemeChange);
  }

  const listStudyStates = () => {
    return safeKeys()
      .filter((key) => key.startsWith(storagePrefix))
      .map((key) => parseJson(safeGet(key)))
      .filter(Boolean)
      .sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
  };

  const renderResumePanel = () => {
    const panel = document.getElementById('resume-panel');
    if (!panel) {
      return;
    }

    const latest = listStudyStates()[0];
    if (!latest) {
      panel.hidden = true;
      return;
    }

    const pending = Array.isArray(latest.queue) ? latest.queue.length : Number(latest.remaining || 0);
    const mastered = Number(latest.mastered || 0);
    const review = Number(latest.review || 0);
    const href = addHash(latest.url || '#', 'study');

    panel.hidden = false;
    panel.innerHTML = `
      <div class="resume-card">
        <div class="resume-card__copy">
          <p class="resume-card__eyebrow">继续上次学习</p>
          <h2>${escapeHtml(stripMd(latest.title || '最近词表'))}</h2>
          <p>${pending} 个待学 · ${mastered} 个已掌握 · ${review} 个需复习</p>
        </div>
        <a class="action-button" href="${escapeHtml(href)}">继续学习</a>
      </div>
    `;
  };

  const enhanceCategoryPage = () => {
    const markdown = document.querySelector('.markdown-body');
    const table = markdown?.querySelector('table');
    if (!markdown || !table) {
      return;
    }

    const headerCells = Array.from(table.querySelectorAll('thead th'));
    const headers = headerCells.map((cell) => normalize(cell.textContent));
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    if (!rows.length) {
      return;
    }

    const fileIndex = headers.findIndex((header) => /文件|词表|单词/.test(header));
    if (fileIndex < 0) {
      return;
    }

    const wrapper = document.createElement('section');
    wrapper.className = 'catalog-section';

    const intro = document.createElement('div');
    intro.className = 'catalog-section__intro';
    intro.innerHTML = `
      <p class="eyebrow">分类首页</p>
      <h2>选择一本教材后开始学习</h2>
    `;

    const grid = document.createElement('div');
    grid.className = 'catalog-grid catalog-grid--category';

    rows.forEach((row) => {
      const cells = Array.from(row.querySelectorAll('td'));
      const fileCell = cells[fileIndex] || cells[0];
      const primaryLink = fileCell?.querySelector('a') || row.querySelector('a');
      if (!primaryLink) {
        return;
      }

      const title = stripMd(primaryLink.textContent || fileCell?.textContent || '');
      const eyebrow = fileIndex > 0 ? normalize(cells[0]?.textContent) : '';
      const meta = cells
        .map((cell, index) => {
          if (index === fileIndex || (fileIndex > 0 && index === 0)) {
            return '';
          }
          return normalize(cell.textContent);
        })
        .filter(Boolean);
      const browseHref = primaryLink.href;
      const studyHref = addHash(browseHref, 'study');

      const card = document.createElement('article');
      card.className = 'catalog-card';
      card.innerHTML = `
        ${eyebrow ? `<div class="catalog-card__eyebrow">${escapeHtml(eyebrow)}</div>` : ''}
        <h3 class="catalog-card__title">${escapeHtml(title)}</h3>
        ${meta.length ? `<div class="catalog-card__meta">${meta.map((item) => `<span>${escapeHtml(item)}</span>`).join('')}</div>` : ''}
        <div class="catalog-card__actions">
          <a class="button-secondary" href="${escapeHtml(browseHref)}">浏览词表</a>
          <a class="action-button" href="${escapeHtml(studyHref)}">开始学习</a>
        </div>
      `;

      grid.appendChild(card);
    });

    table.insertAdjacentElement('beforebegin', wrapper);
    wrapper.appendChild(intro);
    wrapper.appendChild(grid);
    table.remove();
  };

  const enhanceVocabPage = () => {
    const markdown = document.querySelector('.markdown-body');
    if (!markdown) {
      return;
    }

    const tables = Array.from(markdown.querySelectorAll('table'));
    const table = tables.find((candidate) => {
      const headers = Array.from(candidate.querySelectorAll('thead th')).map((cell) => normalize(cell.textContent));
      return headers.some((header) => header.includes('单词')) && headers.some((header) => header.includes('中文'));
    });

    if (!table) {
      return;
    }

    const headers = Array.from(table.querySelectorAll('thead th')).map((cell) => normalize(cell.textContent));
    const pickIndex = (matcher) => headers.findIndex(matcher);
    const indexMap = {
      word: pickIndex((header) => header === '单词' || header.includes('单词')),
      uk: pickIndex((header) => header.includes('英式')),
      us: pickIndex((header) => header.includes('美式')),
      zh: pickIndex((header) => header.includes('中文翻译') || header.includes('释义') || (header.includes('中文') && !header.includes('例句'))),
      example: pickIndex((header) => header === '例句' || (header.includes('例句') && !header.includes('翻译'))),
      translation: pickIndex((header) => header.includes('例句翻译') || header === '翻译'),
    };

    if (indexMap.word < 0 || indexMap.zh < 0) {
      return;
    }

    const deck = Array.from(table.querySelectorAll('tbody tr'))
      .map((row, index) => {
        const cells = Array.from(row.querySelectorAll('td'));
        const read = (cellIndex) => normalize(cells[cellIndex]?.textContent);
        const entry = {
          no: read(0) || String(index + 1),
          word: read(indexMap.word),
          uk: read(indexMap.uk),
          us: read(indexMap.us),
          zh: read(indexMap.zh),
          example: read(indexMap.example),
          translation: read(indexMap.translation),
        };

        return entry;
      })
      .filter((entry) => entry.word);

    if (!deck.length) {
      return;
    }

    const deckTitle = normalize(markdown.querySelector('h1')?.textContent || document.title);
    const deckUrl = window.location.href.split('#')[0];
    const storageKey = `${storagePrefix}${deckUrl}`;
    const defaultState = () => ({
      queue: deck.map((_, index) => index),
      mastered: 0,
      review: 0,
      revealed: true,
      updatedAt: Date.now(),
      title: deckTitle,
      url: deckUrl,
      total: deck.length,
    });

    const savedState = parseJson(safeGet(storageKey));
    const state = savedState && Array.isArray(savedState.queue) && savedState.total === deck.length
      ? {
          queue: savedState.queue.filter((value) => Number.isInteger(value) && value >= 0 && value < deck.length),
          mastered: Number(savedState.mastered || 0),
          review: Number(savedState.review || 0),
          revealed: window.location.hash === '#study' ? true : Boolean(savedState.revealed),
          updatedAt: Number(savedState.updatedAt || Date.now()),
          title: deckTitle,
          url: deckUrl,
          total: deck.length,
        }
      : defaultState();

    const studyShell = document.createElement('section');
    studyShell.className = 'study-shell';
    studyShell.id = 'study';
    studyShell.setAttribute('tabindex', '-1');
    studyShell.innerHTML = `
      <div class="study-shell__top">
        <div class="study-shell__heading">
          <p class="eyebrow">开始学习</p>
          <h2>${escapeHtml(deckTitle)}</h2>
        </div>
        <div class="study-shell__meta">
          <span data-study-progress></span>
        </div>
      </div>
      <div class="study-shell__card">
        <div class="study-shell__word" data-study-word></div>
        <div class="study-shell__phonetics">
          <span data-study-uk></span>
          <span data-study-us></span>
        </div>
        <div class="study-shell__answer" data-study-answer hidden>
          <p class="study-shell__zh" data-study-zh></p>
          <p class="study-shell__example" data-study-example></p>
          <p class="study-shell__translation" data-study-translation></p>
        </div>
        <div class="study-shell__actions">
          <button class="button-secondary" type="button" data-study-reveal>显示释义</button>
          <button class="ghost-button" type="button" data-study-reset>重置</button>
          <button class="button-secondary" type="button" data-study-hard>不熟</button>
          <button class="action-button" type="button" data-study-known>掌握</button>
        </div>
        <div class="study-shell__stats" data-study-stats></div>
      </div>
    `;

    table.insertAdjacentElement('beforebegin', studyShell);

    const nodes = {
      progress: studyShell.querySelector('[data-study-progress]'),
      word: studyShell.querySelector('[data-study-word]'),
      uk: studyShell.querySelector('[data-study-uk]'),
      us: studyShell.querySelector('[data-study-us]'),
      answer: studyShell.querySelector('[data-study-answer]'),
      zh: studyShell.querySelector('[data-study-zh]'),
      example: studyShell.querySelector('[data-study-example]'),
      translation: studyShell.querySelector('[data-study-translation]'),
      reveal: studyShell.querySelector('[data-study-reveal]'),
      reset: studyShell.querySelector('[data-study-reset]'),
      hard: studyShell.querySelector('[data-study-hard]'),
      known: studyShell.querySelector('[data-study-known]'),
      stats: studyShell.querySelector('[data-study-stats]'),
    };

    const persistState = () => {
      state.updatedAt = Date.now();
      state.title = deckTitle;
      state.url = deckUrl;
      state.total = deck.length;
      safeSet(storageKey, JSON.stringify(state));
    };

    const render = () => {
      const currentIndex = state.queue[0];
      const current = deck[currentIndex];
      const completed = state.queue.length === 0;
      const progressText = `${Math.min(deck.length - state.queue.length, deck.length)}/${deck.length}`;

      nodes.progress.textContent = progressText;
      nodes.stats.textContent = completed
        ? `已掌握 ${state.mastered} · 需复习 ${state.review}`
        : `已掌握 ${state.mastered} · 需复习 ${state.review}`;

      if (!current) {
        nodes.word.textContent = '完成本轮';
        nodes.uk.textContent = '';
        nodes.us.textContent = '';
        nodes.answer.hidden = false;
        nodes.zh.textContent = '当前词表已学完。';
        nodes.example.textContent = '点击“重置”重新开始。';
        nodes.translation.textContent = '';
        nodes.reveal.disabled = true;
        nodes.hard.disabled = true;
        nodes.known.disabled = true;
        nodes.reveal.textContent = '显示释义';
        return;
      }

      nodes.word.textContent = current.word;
      nodes.uk.textContent = current.uk ? `UK ${current.uk}` : '';
      nodes.us.textContent = current.us ? `US ${current.us}` : '';
      nodes.answer.hidden = !state.revealed;
      nodes.zh.textContent = current.zh;
      nodes.example.textContent = current.example ? current.example : ' ';
      nodes.translation.textContent = current.translation ? current.translation : ' ';
      nodes.reveal.disabled = false;
      nodes.hard.disabled = false;
      nodes.known.disabled = false;
      nodes.reveal.textContent = state.revealed ? '收起释义' : '显示释义';
    };

    const revealAnswer = () => {
      if (!state.queue.length) {
        return;
      }
      state.revealed = !state.revealed;
      persistState();
      render();
    };

    const resetStudy = () => {
      state.queue = deck.map((_, index) => index);
      state.mastered = 0;
      state.review = 0;
      state.revealed = true;
      persistState();
      render();
      studyShell.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const markKnown = () => {
      if (!state.queue.length) {
        return;
      }

      state.queue.shift();
      state.mastered += 1;
      state.revealed = true;
      persistState();
      render();
    };

    const markHard = () => {
      if (!state.queue.length) {
        return;
      }

      const current = state.queue.shift();
      state.queue.push(current);
      state.review += 1;
      state.revealed = true;
      persistState();
      render();
    };

    nodes.reveal.addEventListener('click', revealAnswer);
    nodes.reset.addEventListener('click', resetStudy);
    nodes.hard.addEventListener('click', markHard);
    nodes.known.addEventListener('click', markKnown);

    render();
    persistState();

    if (window.location.hash === '#study') {
      requestAnimationFrame(() => {
        studyShell.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  };

  if (pageKind === 'home') {
    renderResumePanel();
  } else if (pageKind === 'category') {
    enhanceCategoryPage();
  } else if (pageKind === 'vocab') {
    enhanceVocabPage();
  }
});
