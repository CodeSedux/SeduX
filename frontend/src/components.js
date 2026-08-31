export function createHeader({ title, subtitle }) {
  const header = document.createElement('header');
  header.className = 'topbar';

  const brand = document.createElement('div');
  brand.className = 'brand';
  brand.innerHTML = `
    <div class="brand-mark">S</div>
    <div>
      <div class="brand-name">${title}</div>
      <div class="brand-subtitle">${subtitle}</div>
    </div>
  `;

  const toolbar = document.createElement('div');
  toolbar.className = 'toolbar';
  toolbar.innerHTML = `
    <button class="ghost-button">Overview</button>
    <button class="primary-button">Deploy</button>
  `;

  header.append(brand, toolbar);
  return header;
}

export function createSidebar(items) {
  const aside = document.createElement('aside');
  aside.className = 'sidebar';

  const title = document.createElement('div');
  title.className = 'nav-title';
  title.textContent = 'Navigation';
  aside.appendChild(title);

  items.forEach((item) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `nav-item ${item.active ? 'active' : ''}`;
    button.dataset.view = item.view;
    button.setAttribute('aria-current', item.active ? 'page' : 'false');
    button.innerHTML = `
      <span class="nav-icon">${item.icon}</span>
      <span>${item.label}</span>
    `;
    aside.appendChild(button);
  });

  return aside;
}

export function createStatCard({ label, value, delta, tone = 'blue' }) {
  const article = document.createElement('article');
  article.className = 'stat-card';
  article.innerHTML = `
    <div class="stat-label">${label}</div>
    <div class="stat-value">${value}</div>
    <div class="stat-delta ${tone}">${delta}</div>
  `;

  return article;
}

export function createServiceList(services) {
  const section = document.createElement('section');
  section.className = 'panel';

  const heading = document.createElement('div');
  heading.className = 'panel-header';
  heading.innerHTML = `
    <h2>Service status</h2>
    <span class="status-pill online">Online</span>
  `;

  const list = document.createElement('div');
  list.className = 'service-list';

  services.forEach((service) => {
    const row = document.createElement('div');
    row.className = 'service-row';
    row.innerHTML = `
      <div class="service-meta">
        <div class="service-name">${service.name}</div>
        <div class="service-kind">${service.kind}</div>
      </div>
      <div class="service-tag ${service.status === 'healthy' ? 'healthy' : 'degraded'}">
        ${service.status}
      </div>
    `;
    list.appendChild(row);
  });

  section.append(heading, list);
  return section;
}

export function createActivityFeed(items) {
  const section = document.createElement('section');
  section.className = 'panel';

  const heading = document.createElement('div');
  heading.className = 'panel-header';
  heading.innerHTML = `
    <h2>Recent activity</h2>
    <span class="muted-link">Live</span>
  `;

  const list = document.createElement('ul');
  list.className = 'activity-feed';

  items.forEach((item) => {
    const entry = document.createElement('li');
    entry.innerHTML = `
      <span class="activity-time">${item.time}</span>
      <span class="activity-copy">${item.message}</span>
    `;
    list.appendChild(entry);
  });

  section.append(heading, list);
  return section;
}

export function createCommandPanel(actions) {
  const panel = document.createElement('section');
  panel.className = 'panel';

  const heading = document.createElement('div');
  heading.className = 'panel-header';
  heading.innerHTML = `
    <h2>Quick actions</h2>
    <span class="muted-link">Tasks</span>
  `;

  const stack = document.createElement('div');
  stack.className = 'action-stack';

  actions.forEach((action) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'action-button';
    button.textContent = action;
    stack.appendChild(button);
  });

  panel.append(heading, stack);
  return panel;
}
