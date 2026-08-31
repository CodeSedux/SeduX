function createPanel(title, eyebrow, content) {
  const section = document.createElement('section');
  section.className = 'view-panel panel';
  section.innerHTML = `<div class="panel-header"><div><div class="eyebrow">${eyebrow}</div><h2>${title}</h2></div></div>`;
  section.appendChild(content);
  return section;
}

function createList(items, className = 'detail-list') {
  const list = document.createElement('div');
  list.className = className;
  items.forEach((item) => {
    const row = document.createElement('div');
    row.className = 'detail-row';
    row.innerHTML = `<div><strong>${item.title}</strong><span>${item.detail}</span></div><span class="status-tag ${item.tone || ''}">${item.status}</span>`;
    list.appendChild(row);
  });
  return list;
}

export function normalizeConsentKey(label) {
  return String(label || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

export function getConsentRows(state = {}) {
  const consent = state.consent || {};
  const definitions = [
    {
      key: 'device_controls',
      label: 'Device controls',
      description: 'Allow SeduX to inspect and control connected devices.',
      checked: Boolean(consent.devices),
    },
    {
      key: 'voice_processing',
      label: 'Voice processing',
      description: 'Allow voice sessions to use the local pipeline.',
      checked: Boolean(consent.voice),
    },
    {
      key: 'screen_access',
      label: 'Screen access',
      description: 'Allow read-only screen capture and confirmation-based automation.',
      checked: Boolean(consent.screen),
    },
  ];
  return definitions.map((definition) => ({
    ...definition,
    key: definition.key || normalizeConsentKey(definition.label),
  }));
}

export function renderOverview(state) {
  const fragment = document.createDocumentFragment();
  const stats = document.createElement('div');
  stats.className = 'stats-grid';
  state.stats.forEach((stat) => {
    const card = document.createElement('article');
    card.className = 'stat-card';
    card.innerHTML = `<div class="stat-label">${stat.label}</div><div class="stat-value">${stat.value}</div><div class="stat-delta ${stat.tone}">${stat.delta}</div>`;
    stats.appendChild(card);
  });
  fragment.appendChild(stats);
  fragment.appendChild(createPanel('Recent activity', 'Live feed', createList(state.activity.map((item) => ({ ...item, title: item.time, detail: item.message, status: 'logged', tone: 'blue' })))));
  return fragment;
}

export function renderChat(state, onSubmit) {
  const content = document.createElement('div');
  content.className = 'chat-layout';
  const messages = document.createElement('div');
  messages.className = 'chat-messages';
  state.messages.forEach((message) => {
    const bubble = document.createElement('div');
    bubble.className = `message ${message.role}`;
    bubble.innerHTML = `<span class="message-role">${message.role === 'assistant' ? 'SeduX' : 'You'}</span><p>${message.text}</p>`;
    messages.appendChild(bubble);
  });
  const form = document.createElement('form');
  form.className = 'chat-form';
  form.innerHTML = '<label for="chat-input">Message</label><div><input id="chat-input" name="message" placeholder="Ask SeduX something..." autocomplete="off" /><button class="primary-button" type="submit">Send</button></div>';
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const input = form.elements.message;
    if (input.value.trim()) onSubmit(input.value.trim());
  });
  content.append(messages, form);
  return createPanel('Conversation', 'Assistant workspace', content);
}

export function renderServices(state) {
  const content = document.createElement('div');
  content.appendChild(createList(state.services.map((service) => ({
    title: service.name,
    detail: `${service.kind} · port ${service.port || 'managed'}`,
    status: service.status,
    tone: service.status === 'healthy' ? 'green' : 'amber',
  }))));
  return createPanel('Service registry', 'Gateway integration', content);
}

export function renderTasks(state) {
  const content = document.createElement('div');
  content.appendChild(createList(state.tasks.map((task) => ({
    title: task.name,
    detail: `${task.schedule} · ${task.owner}`,
    status: task.status,
    tone: task.status === 'queued' ? 'blue' : 'green',
  }))));
  return createPanel('Task manager', 'Scheduling and execution', content);
}

export function renderHome(state) {
  const content = document.createElement('div');
  content.appendChild(createList(state.devices.map((device) => ({
    title: device.name,
    detail: `${device.room} · ${device.type}`,
    status: device.status,
    tone: device.status === 'online' ? 'green' : 'amber',
  }))));
  return createPanel('Home control', 'Device overview', content);
}

export function renderScreen() {
  const content = document.createElement('div');
  content.className = 'empty-state';
  content.innerHTML = '<div class="empty-icon">▣</div><h3>Screen access is paused</h3><p>Read-only capture becomes available after explicit consent.</p><button class="ghost-button" type="button">Review consent</button>';
  return createPanel('Screen automation', 'Safety boundary', content);
}

export function renderSettings(state, onConsentChange) {
  const content = document.createElement('div');
  content.className = 'settings-form';
  const rows = getConsentRows(state);

  rows.forEach((row) => {
    const label = document.createElement('label');
    label.className = 'setting-row';
    label.innerHTML = `
      <span>
        <strong>${row.label}</strong>
        <small>${row.description}</small>
      </span>
      <input type="checkbox" data-consent-key="${row.key}" ${row.checked ? 'checked' : ''} />
    `;
    label.querySelector('input').addEventListener('change', () => {
      onConsentChange?.(row.key, label.querySelector('input').checked);
    });
    content.appendChild(label);
  });

  return createPanel('Settings', 'Consent and privacy', content);
}
