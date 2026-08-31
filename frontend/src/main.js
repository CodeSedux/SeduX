import './styles.css';

const root = document.getElementById('root');

const featureCards = [
  {
    tag: 'Available now',
    title: 'Adaptive AI voice assistant',
    text: 'Natural conversations, voice-first commands, and live response orchestration for everyday tasks and device control.',
    accent: 'blue',
  },
  {
    tag: 'Available now',
    title: 'Emotion-aware interaction',
    text: 'Contextual tone, sentiment awareness, and calm escalation patterns that adapt to user need and household rhythm.',
    accent: 'purple',
  },
  {
    tag: 'Available now',
    title: 'Smart home orchestration',
    text: 'Secure automation for lights, climate, access, routines, and household flows with explicit consent and review.',
    accent: 'green',
  },
  {
    tag: 'Coming soon',
    title: 'Avatar and media runtime',
    text: 'Deeper embodied experiences with avatar replay, bounded media processing, voice filtering, and multimodal responses.',
    accent: 'amber',
  },
  {
    tag: 'Coming soon',
    title: 'Screen and content safety',
    text: 'Permission-aware previewing, content boundaries, and policy-based screen actions to keep sensitive workflows safe.',
    accent: 'cyan',
  },
  {
    tag: 'Coming soon',
    title: 'Multi-agent task engine',
    text: 'Deferred tasks, priority routing, dead-letter handling, and resilient retries across device and services layers.',
    accent: 'slate',
  },
];

const roadmap = [
  { phase: 'Control plane', status: 'In place', detail: 'Health, readiness, request IDs, observability, and service coordination.' },
  { phase: 'Emotion + voice', status: 'Active', detail: 'Adaptive tone models, bounded audio, and contextual replies.' },
  { phase: 'Safe actions', status: 'In progress', detail: 'Confirmation flows, audit trails, stale-state protections, and kill switches.' },
  { phase: 'Production integrations', status: 'Planned', detail: 'PostgreSQL, Redis, model adapters, MQTT, Home Assistant, and external services.' },
];

const legalSections = [
  {
    title: 'Terms of service',
    text: 'Use SeduX only for lawful, consented, and transparent interactions. We provide the service as-is with operational safeguards and explicit user controls.',
  },
  {
    title: 'Privacy policy',
    text: 'We minimize collection, separate ephemeral cache from durable user data, and explain how consent, retention, and access are managed.',
  },
  {
    title: 'Acceptable use',
    text: 'No harassment, covert surveillance, abusive device control, unauthorized access, malware, or harmful automation attempts are allowed.',
  },
  {
    title: 'Data rights',
    text: 'Users can review, correct, delete, or export personal data where applicable, subject to legal obligations and safety constraints.',
  },
  {
    title: 'IP & licensing',
    text: 'The platform and product materials remain protected by copyright and applicable licenses; third-party model integrations must retain provenance and relevant terms.',
  },
  {
    title: 'Security & compliance',
    text: 'We apply least-privilege access, audits, consent gating, and incident recovery processes to keep sensitive actions constrained and reviewable.',
  },
];

root.innerHTML = `
  <div class="page-shell">
    <header class="site-header">
      <div class="container nav-wrap">
        <div class="brand-block" aria-label="SeduX home">
          <div class="brand-mark">S</div>
          <div>
            <div class="brand-name">SeduX</div>
            <div class="brand-tag">AI control plane</div>
          </div>
        </div>
        <nav class="main-nav" aria-label="Main navigation">
          <a href="#features">Features</a>
          <a href="#roadmap">Roadmap</a>
          <a href="#experience">Experience</a>
          <a href="#legal">Legal</a>
        </nav>
        <div class="nav-actions">
          <button class="btn btn-ghost">Log in</button>
          <button class="btn btn-primary">Get started</button>
        </div>
      </div>
    </header>

    <main>
      <section class="hero-section">
        <div class="container hero-grid">
          <div class="hero-copy">
            <span class="eyebrow">Human-centered AI orchestration</span>
            <h1>Build calmer, safer, smarter digital experiences for every user.</h1>
            <p>
              SeduX blends voice, emotion, home control, tasks, and screen safety into one secure operating layer for personal and household AI experiences.
            </p>
            <div class="cta-row">
              <button class="btn btn-primary">Start with SeduX</button>
              <button class="btn btn-ghost">View roadmap</button>
            </div>
            <div class="trust-row" aria-label="Trust indicators">
              <span><strong>99.2%</strong> service health</span>
              <span><strong>42</strong> active devices</span>
              <span><strong>24/7</strong> safety oversight</span>
            </div>
          </div>

          <div class="hero-panel" aria-label="Overview panel">
            <div class="signal-row">
              <span class="signal-dot"></span>
              <span>System pulse</span>
              <span class="chip chip-success">Healthy</span>
            </div>

            <div class="hero-card hero-card-primary">
              <div>
                <p class="card-label">Current status</p>
                <h3>Household orchestration</h3>
              </div>
              <div class="metric">128</div>
              <span class="metric-label">Tasks handled today</span>
            </div>

            <div class="mini-grid">
              <div class="mini-card">
                <span class="mini-label">Voice</span>
                <strong>Ready</strong>
              </div>
              <div class="mini-card">
                <span class="mini-label">Emotion</span>
                <strong>Adaptive</strong>
              </div>
              <div class="mini-card">
                <span class="mini-label">Home</span>
                <strong>Secure</strong>
              </div>
              <div class="mini-card">
                <span class="mini-label">Safety</span>
                <strong>Guarded</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="stats-section">
        <div class="container stats-grid" aria-label="Key platform stats">
          <article class="stat-card">
            <span class="stat-label">Health</span>
            <strong>99.2%</strong>
            <small class="positive">+1.2% vs last week</small>
          </article>
          <article class="stat-card">
            <span class="stat-label">Latency</span>
            <strong>134ms</strong>
            <small class="positive">-18ms improvement</small>
          </article>
          <article class="stat-card">
            <span class="stat-label">Active devices</span>
            <strong>42</strong>
            <small>Across home and office</small>
          </article>
          <article class="stat-card">
            <span class="stat-label">Tasks</span>
            <strong>128</strong>
            <small class="positive">+8 today</small>
          </article>
        </div>
      </section>

      <section id="features" class="section-block">
        <div class="container">
          <div class="heading-row">
            <div>
              <span class="eyebrow">Available and coming</span>
              <h2>Everything users need to orchestrate AI in one experience.</h2>
            </div>
            <p>From personal assistants to household automation, SeduX is designed to be safe, clear, and adaptable.</p>
          </div>

          <div class="feature-grid">
            ${featureCards
              .map(
                (feature) => `
                  <article class="feature-card ${feature.accent}">
                    <div class="feature-topline">
                      <span class="feature-tag ${feature.accent}">${feature.tag}</span>
                    </div>
                    <h3>${feature.title}</h3>
                    <p>${feature.text}</p>
                  </article>
                `,
              )
              .join('')}
          </div>
        </div>
      </section>

      <section id="roadmap" class="section-block alt-block">
        <div class="container">
          <div class="heading-row narrow">
            <div>
              <span class="eyebrow">Delivery roadmap</span>
              <h2>Planned evolution of the platform.</h2>
            </div>
          </div>

          <div class="timeline">
            ${roadmap
              .map(
                (item) => `
                  <article class="timeline-item">
                    <span class="timeline-phase">${item.phase}</span>
                    <div class="timeline-body">
                      <span class="timeline-status">${item.status}</span>
                      <p>${item.detail}</p>
                    </div>
                  </article>
                `,
              )
              .join('')}
          </div>
        </div>
      </section>

      <section id="experience" class="section-block">
        <div class="container">
          <div class="heading-row">
            <div>
              <span class="eyebrow">User experience</span>
              <h2>Designed for clarity, trust, and control.</h2>
            </div>
          </div>

          <div class="experience-grid">
            <div class="experience-card">
              <span class="experience-icon">01</span>
              <h3>Speak naturally</h3>
              <p>Voice-first prompts, contextual follow-up, and smooth ambient interaction across tasks and home routines.</p>
            </div>
            <div class="experience-card">
              <span class="experience-icon">02</span>
              <h3>Review before action</h3>
              <p>Critical operations require confirmation, audit review, and user awareness before high-impact automation runs.</p>
            </div>
            <div class="experience-card">
              <span class="experience-icon">03</span>
              <h3>Stay in control</h3>
              <p>Consent toggles, digital rights, retention settings, and privacy choices make the system easy to trust.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="legal" class="section-block alt-block">
        <div class="container">
          <div class="heading-row narrow">
            <div>
              <span class="eyebrow">Legal, policy, and rights</span>
              <h2>Clear rules for safe, respectful, and transparent usage.</h2>
            </div>
          </div>

          <div class="legal-grid">
            ${legalSections
              .map(
                (item) => `
                  <article class="legal-card">
                    <div class="legal-head">
                      <span class="legal-bullet"></span>
                      <h3>${item.title}</h3>
                    </div>
                    <p>${item.text}</p>
                  </article>
                `,
              )
              .join('')}
          </div>

          <div class="policy-box">
            <div>
              <span class="eyebrow">Rights and usage summary</span>
              <h3>User rights and platform guardrails</h3>
            </div>
            <ul>
              <li>Users can review consent choices, request data access or correction, and control how personal automation is used.</li>
              <li>Services must respect privacy, safety boundaries, and applicable laws when processing personal or household data.</li>
              <li>Commercial use, model integrations, and outbound actions require clear disclosure, provenance, and retention controls.</li>
              <li>All platform content, service interfaces, and design materials are subject to intellectual property, licensing, and security protections.</li>
            </ul>
          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container footer-wrap">
        <div>
          <div class="brand-block">
            <div class="brand-mark">S</div>
            <div>
              <div class="brand-name">SeduX</div>
              <div class="brand-tag">AI for safer digital life</div>
            </div>
          </div>
        </div>
        <div class="footer-links">
          <a href="#features">Features</a>
          <a href="#roadmap">Roadmap</a>
          <a href="#legal">Privacy</a>
          <a href="#legal">Terms</a>
        </div>
        <p>© 2026 SeduX. All rights reserved.</p>
      </div>
    </footer>
  </div>
`;
