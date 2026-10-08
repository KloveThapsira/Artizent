import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Upload, GitBranch, Rocket, CheckCircle, AlertTriangle,
  ExternalLink, Terminal, Copy, Check, Search, Code,
  Package, Wrench, Globe, Zap, FolderOpen, X,
  Key, ShieldCheck, ChevronDown, ChevronUp
} from 'lucide-react';
import './style.css';

/* ═══════════════════════════════════════════
   TOKEN GUIDE DATA
═══════════════════════════════════════════ */
const PLATFORMS = [
  {
    id: 'netlify',
    name: 'Netlify',
    token: 'NETLIFY_AUTH_TOKEN',
    color: '#00c7b7',
    bg: 'rgba(0,199,183,0.12)',
    border: 'rgba(0,199,183,0.3)',
    emoji: '🟦',
    url: 'https://app.netlify.com',
    usedFor: ['HTML/CSS/JS', 'React', 'Vite', 'Vue', 'Angular'],
    steps: [
      'Login to https://app.netlify.com',
      'Click your Profile Icon (top right)',
      'Open User Settings',
      'Select Applications',
      'Scroll to Personal Access Tokens',
      'Click Create Personal Access Token',
      'Enter a token name & click Generate',
      'Copy the token immediately',
      'Paste it into AutoDeploy Agent',
    ],
    cli: 'npm install -g netlify-cli',
    verify: 'netlify --version',
  },
  {
    id: 'vercel',
    name: 'Vercel',
    token: 'VERCEL_TOKEN',
    color: '#ffffff',
    bg: 'rgba(255,255,255,0.07)',
    border: 'rgba(255,255,255,0.2)',
    emoji: '▲',
    url: 'https://vercel.com',
    usedFor: ['Next.js', 'React', 'Vite', 'Frontend Apps'],
    steps: [
      'Login to https://vercel.com',
      'Open Account Settings (top-right avatar)',
      'Navigate to the Tokens section',
      'Click Create Token',
      'Enter a token name',
      'Click Generate Token',
      'Copy the token',
      'Paste into AutoDeploy Agent',
    ],
    cli: 'npm install -g vercel',
    verify: 'vercel --version',
  },
  {
    id: 'railway',
    name: 'Railway',
    token: 'RAILWAY_TOKEN',
    color: '#b975f9',
    bg: 'rgba(185,117,249,0.12)',
    border: 'rgba(185,117,249,0.3)',
    emoji: '🚂',
    url: 'https://railway.app',
    usedFor: ['Node.js', 'Express.js', 'Flask', 'FastAPI', 'Django', 'Spring Boot', 'MERN'],
    steps: [
      'Login to https://railway.app',
      '⚠️ You need a PROJECT Token, not an Account Token',
      'Open your Railway project (create one if needed)',
      'Go to Project Settings (⚙️ icon in the project)',
      'Click the Tokens tab',
      'Click Create Token',
      'Enter a name and click Generate',
      'Copy the token immediately',
      'Paste into AutoDeploy Agent',
    ],
    note: 'IMPORTANT: Use a Project Token (from Project Settings → Tokens), NOT an Account/Workspace token. Account tokens cannot deploy without interactive setup.',
    cli: 'npm install -g @railway/cli',
    verify: 'railway --version',
  },
  {
    id: 'render',
    name: 'Render',
    token: 'RENDER_API_KEY',
    color: '#46e3b7',
    bg: 'rgba(70,227,183,0.10)',
    border: 'rgba(70,227,183,0.3)',
    emoji: '☁️',
    url: 'https://dashboard.render.com',
    usedFor: ['Flask', 'FastAPI', 'Django', 'Express.js', 'Docker Apps'],
    steps: [
      'Login to https://dashboard.render.com',
      'Open Account Settings',
      'Navigate to API Keys',
      'Click Create API Key',
      'Enter a name',
      'Click Generate Key',
      'Copy the key',
      'Paste into AutoDeploy Agent',
    ],
    cli: null,
    verify: null,
    note: 'Render deployment can also be done manually using render.yaml placed in your project root.',
  },
  {
    id: 'azure',
    name: 'Azure',
    token: 'Azure Login Session',
    color: '#00a4ef',
    bg: 'rgba(0,164,239,0.10)',
    border: 'rgba(0,164,239,0.3)',
    emoji: '☁',
    url: 'https://portal.azure.com',
    usedFor: ['ASP.NET Core', '.NET Web API', 'Java Enterprise'],
    steps: [
      'Create an Azure Account at https://portal.azure.com',
      'Install Azure CLI from https://learn.microsoft.com/cli/azure/install-azure-cli',
      'Open a terminal and run: az login',
      'Complete browser authentication that opens',
      'Verify with: az account show',
      'AutoDeploy Agent will use your active login session',
    ],
    cli: 'az login',
    verify: 'az account show',
    note: 'No token required. AutoDeploy Agent uses your existing Azure CLI session.',
  },
];

/* ── Token Guide Component ── */
function TokenGuide() {
  const [active, setActive] = useState('netlify');
  const [open, setOpen] = useState(false);
  const p = PLATFORMS.find(x => x.id === active);

  return (
    <div className="card glass tg-wrap">
      {/* Header — click to expand/collapse */}
      <button className="tg-header" onClick={() => setOpen(o => !o)}>
        <div className="tg-header-left">
          <div className="card-ico" style={{ background: 'rgba(251,191,36,0.15)', border: '1px solid rgba(251,191,36,0.3)', color: '#fbbf24' }}>
            <Key size={18}/>
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: 18 }}>Deployment Token Guide</h2>
            <p className="tg-subtitle">How to get your platform token for Real Deployment Mode</p>
          </div>
        </div>
        <span className="tg-chevron">
          {open ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
        </span>
      </button>

      {open && (
        <div className="tg-body">
          {/* Platform Tabs */}
          <div className="tg-tabs">
            {PLATFORMS.map(pl => (
              <button
                key={pl.id}
                className={`tg-tab ${active === pl.id ? 'tg-tab-active' : ''}`}
                style={active === pl.id ? { borderColor: pl.border, color: pl.color, background: pl.bg } : {}}
                onClick={() => setActive(pl.id)}
              >
                <span>{pl.emoji}</span> {pl.name}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="tg-content">
            {/* Left: Steps */}
            <div className="tg-left">
              <div className="tg-section-label">📋 Steps to Get Token</div>
              <ol className="tg-steps">
                {p.steps.map((step, i) => (
                  <li key={i} className="tg-step">
                    <span className="tg-num" style={{ background: p.bg, border: `1px solid ${p.border}`, color: p.color }}>{i + 1}</span>
                    <span className="tg-step-text">{step}</span>
                  </li>
                ))}
              </ol>

              {p.note && (
                <div className="tg-note">
                  💡 {p.note}
                </div>
              )}

              <a
                href={p.url}
                target="_blank"
                rel="noreferrer"
                className="tg-link"
                style={{ borderColor: p.border, color: p.color }}
              >
                Open {p.name} Dashboard <ExternalLink size={14}/>
              </a>
            </div>

            {/* Right: Info */}
            <div className="tg-right">
              {/* Used For */}
              <div className="tg-box">
                <div className="tg-section-label">🚀 Used For</div>
                <div className="tg-tags">
                  {p.usedFor.map(f => (
                    <span key={f} className="tg-tag" style={{ background: p.bg, border: `1px solid ${p.border}`, color: p.color }}>{f}</span>
                  ))}
                </div>
              </div>

              {/* Token name */}
              <div className="tg-box">
                <div className="tg-section-label">🔑 Token / Key Name</div>
                <div className="tg-code-row">
                  <code className="tg-code">{p.token}</code>
                  <CopyButton text={p.token}/>
                </div>
              </div>

              {/* CLI */}
              {p.cli && (
                <div className="tg-box">
                  <div className="tg-section-label">⚙️ Required CLI</div>
                  <div className="tg-code-row">
                    <code className="tg-code">{p.cli}</code>
                    <CopyButton text={p.cli}/>
                  </div>
                </div>
              )}

              {/* Verify */}
              {p.verify && (
                <div className="tg-box">
                  <div className="tg-section-label">✅ Verify Installation</div>
                  <div className="tg-code-row">
                    <code className="tg-code">{p.verify}</code>
                    <CopyButton text={p.verify}/>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Security Notice */}
          <div className="tg-security">
            <div className="tg-sec-header">
              <ShieldCheck size={18} style={{ color: '#4ade80' }}/>
              <strong>Security Notice</strong>
            </div>
            <ul className="tg-sec-list">
              <li>🔒 Tokens are <strong>never stored permanently</strong> in AutoDeploy Agent.</li>
              <li>🙈 Tokens are <strong>masked in deployment logs</strong> so they never appear in plain text.</li>
              <li>⚡ Tokens are <strong>used only during deployment</strong> and discarded immediately after.</li>
              <li>🚫 <strong>Do not share tokens publicly</strong> or commit them to version control.</li>
              <li>🗑️ <strong>Revoke tokens immediately</strong> from the platform dashboard if accidentally exposed.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

const API = 'http://localhost:8000';

const PIPELINE = [
  { key: 'Uploaded',                label: 'Upload',    Icon: Upload,   desc: 'Project received'    },
  { key: 'Analyzing',               label: 'Analyze',   Icon: Search,   desc: 'Scanning codebase'   },
  { key: 'Framework Detected',      label: 'Detect',    Icon: Code,     desc: 'Stack identified'    },
  { key: 'Installing Dependencies', label: 'Install',   Icon: Package,  desc: 'Installing packages' },
  { key: 'Building',                label: 'Build',     Icon: Wrench,   desc: 'Compiling project'   },
  { key: 'Deploying',               label: 'Deploy',    Icon: Rocket,   desc: 'Pushing to cloud'    },
  { key: 'Success',                 label: 'Live',      Icon: Globe,    desc: 'Deployed!'           },
];

/* ── Copy Button ── */
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  function copy() {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }
  return (
    <button className="copy-btn" onClick={copy}>
      {copied ? <Check size={14}/> : <Copy size={14}/>}
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
}

/* ── Pipeline Stepper ── */
function Pipeline({ currentIdx, isFailed }) {
  return (
    <div className="pipeline-wrap">
      {PIPELINE.map((step, i) => {
        let state;
        if (isFailed) {
          state = i < currentIdx ? 'done' : i === currentIdx ? 'error' : 'pending';
        } else {
          state = i < currentIdx ? 'done' : i === currentIdx ? 'active' : 'pending';
        }
        const { Icon, label, desc } = step;
        const isLast = i === PIPELINE.length - 1;

        return (
          <React.Fragment key={step.key}>
            {/* Step Node */}
            <div className={`pipe-step pipe-${state}`}>
              <div className={`pipe-circle pipe-circle-${state}`}>
                {state === 'done'  && <Check size={16}/>}
                {state === 'error' && <X size={16}/>}
                {(state === 'active' || state === 'pending') && <Icon size={16}/>}
                {state === 'active' && <>
                  <span className="pulse-ring ring1"/>
                  <span className="pulse-ring ring2"/>
                </>}
              </div>
              <span className="pipe-label">{label}</span>
              <span className="pipe-desc">{desc}</span>
            </div>

            {/* Connector Line */}
            {!isLast && (
              <div className="pipe-connector-wrap">
                <div className={`pipe-line ${state === 'done' ? 'line-done' : state === 'active' ? 'line-active' : ''}`}>
                  <div className="pipe-line-fill"/>
                </div>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

/* ── Main App ── */
function App() {
  const [projectId, setProjectId]   = useState('');
  const [analysis, setAnalysis]     = useState(null);
  const [token, setToken]           = useState('');
  const [mode, setMode]             = useState('simulation');
  const [logs, setLogs]             = useState('');
  const [liveUrl, setLiveUrl]       = useState('');
  const [status, setStatus]         = useState('Ready');
  const [repoUrl, setRepoUrl]       = useState('');
  const [deployedMode, setDeployedMode] = useState('');
  const [pipelineIdx, setPipelineIdx]   = useState(-1);
  const [isFailed, setIsFailed]         = useState(false);
  const [dragOver, setDragOver]         = useState(false);

  const addLog = (msg) => setLogs(prev => prev + '\n' + msg);

  function updateStatus(s) {
    setStatus(s);
    if (s === 'Failed') {
      setIsFailed(true);
    } else {
      setIsFailed(false);
      const idx = PIPELINE.findIndex(p => p.key === s);
      if (idx >= 0) setPipelineIdx(idx);
    }
  }

  async function handleFile(file) {
    if (!file) return;
    setPipelineIdx(0);
    setIsFailed(false);
    updateStatus('Uploaded');
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch(`${API}/upload`, { method: 'POST', body: form });
      let data;
      try { data = await res.json(); } catch { data = { detail: await res.text() }; }
      if (!res.ok) {
        addLog('Upload error: ' + (data?.detail || `Status ${res.status}`));
        return updateStatus('Failed');
      }
      setProjectId(data.project_id);
      addLog('✓ ZIP uploaded successfully.');
      analyze(data.project_id);
    } catch (err) {
      addLog('Network error: ' + String(err));
      updateStatus('Failed');
    }
  }

  async function submitGithub() {
    if (!repoUrl.trim()) return;
    setIsFailed(false);
    updateStatus('Analyzing');
    try {
      const res = await fetch(`${API}/github`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl })
      });
      const data = await res.json();
      if (!res.ok) return updateStatus('Failed');
      setProjectId(data.project_id);
      setAnalysis(data.analysis);
      updateStatus('Framework Detected');
      addLog('✓ GitHub repo cloned and analyzed.');
    } catch (err) {
      addLog('Network error: ' + String(err));
      updateStatus('Failed');
    }
  }

  async function analyze(id = projectId) {
    updateStatus('Analyzing');
    try {
      const res = await fetch(`${API}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: id })
      });
      const data = await res.json();
      if (!res.ok) return updateStatus('Failed');
      setAnalysis(data);
      updateStatus('Framework Detected');
      addLog('✓ Analysis completed.');
    } catch (err) {
      addLog('Network error: ' + String(err));
      updateStatus('Failed');
    }
  }

  async function deploy() {
    if (!projectId) return;
    setLiveUrl('');
    setDeployedMode(mode);
    updateStatus('Deploying');
    const platform    = analysis?.deployment_plan?.recommended_platform;
    const tokenToSend = mode === 'real' ? token : '';
    try {
      const res = await fetch(`${API}/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, platform, token: tokenToSend, mode })
      });
      const data = await res.json();
      setLogs(data.logs || '');
      updateStatus(data.status || 'Failed');
      if (data.live_url) setLiveUrl(data.live_url);
      if (data.error_explanation) addLog('\n💡 Suggested Fix: ' + data.error_explanation);
      const id = data.project_id || projectId;
      if (id) fetchDeployment(id, !!data.live_url);
    } catch (err) {
      addLog('Network error during deploy: ' + String(err));
      updateStatus('Failed');
    }
  }

  async function fetchDeployment(id, alreadyHasUrl = false) {
    try {
      const res = await fetch(`${API}/deployment/${id}`);
      if (!res.ok) return;
      const d = await res.json();
      if (d.status) updateStatus(d.status);
      if (d.live_url && !alreadyHasUrl) setLiveUrl(d.live_url);
    } catch {/* silent */}
  }

  const plan = analysis?.deployment_plan;
  const isSimulation = deployedMode === 'simulation';

  return (
    <div className="app">
      {/* Ambient background orbs */}
      <div className="orb orb1"/><div className="orb orb2"/><div className="orb orb3"/>

      {/* ── Hero ── */}
      <header className="hero glass">
        <div className="hero-text">
          <span className="hero-badge"><Zap size={11}/> AI-Powered DevOps</span>
          <h1><span className="grad-text">AutoDeploy</span> Agent</h1>
          <p className="hero-sub">
            Drop your ZIP or paste a GitHub URL. AI detects your stack,
            configures, builds, and deploys it in seconds.
          </p>
        </div>
        <div className="hero-rocket-wrap">
          <Rocket size={90} className="hero-rocket"/>
        </div>
      </header>

      {/* ── Input Row ── */}
      <div className="input-grid">
        {/* ZIP Upload */}
        <div className="card glass">
          <div className="card-head">
            <div className="card-ico blue"><Upload size={18}/></div>
            <h2>Upload Project ZIP</h2>
          </div>
          <label
            className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f?.name.endsWith('.zip')) handleFile(f); }}
          >
            <FolderOpen size={40} className="drop-icon"/>
            <span className="drop-main">Drag & drop your ZIP here</span>
            <span className="drop-hint">or click to browse files</span>
            <input type="file" accept=".zip" onChange={e => handleFile(e.target.files[0])} style={{ display:'none' }}/>
          </label>
        </div>

        {/* GitHub */}
        <div className="card glass">
          <div className="card-head">
            <div className="card-ico purple"><GitBranch size={18}/></div>
            <h2>GitHub Repository</h2>
          </div>
          <input
            className="s-input"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            placeholder="https://github.com/user/repo"
            onKeyDown={e => e.key === 'Enter' && submitGithub()}
          />
          <button className="btn-primary" onClick={submitGithub}>
            <GitBranch size={16}/> Clone & Analyze
          </button>
        </div>
      </div>

      {/* ── Pipeline ── */}
      <div className="card glass pipeline-card">
        <div className="pipeline-title-row">
          <Terminal size={17}/>
          <h2 style={{ margin: 0 }}>Deployment Pipeline</h2>
          <span className={`status-pill ${isFailed ? 'pill-fail' : pipelineIdx >= 0 ? 'pill-run' : 'pill-idle'}`}>
            {status}
          </span>
        </div>
        <Pipeline currentIdx={pipelineIdx} isFailed={isFailed}/>
      </div>

      {/* ── Analysis Result ── */}
      {plan && (
        <div className="card glass">
          <div className="card-head">
            <div className="card-ico green"><Code size={18}/></div>
            <h2>Analysis Result</h2>
          </div>
          <div className="info-chips">
            {[
              { k: 'Framework',     v: plan.framework },
              { k: 'Language',      v: plan.language },
              { k: 'Project Type',  v: plan.project_type },
              { k: 'Platform',      v: plan.recommended_platform },
              { k: 'Alternative',   v: plan.alternative_platform },
              { k: 'Build Command', v: plan.build_command || 'No build required' },
              { k: 'Output Folder', v: plan.output_folder || 'Not required' },
              { k: 'Token Needed',  v: plan.token_name },
            ].map(({ k, v }) => (
              <div key={k} className="info-chip">
                <span className="chip-k">{k}</span>
                <span className="chip-v">{v}</span>
              </div>
            ))}
          </div>

          <div className="deploy-section">
            <label className="field-label">Deployment Mode</label>
            <div className="mode-row">
              <button
                className={`mode-btn ${mode === 'simulation' ? 'mode-active' : ''}`}
                onClick={() => setMode('simulation')}
              >🔵 Simulation</button>
              <button
                className={`mode-btn ${mode === 'real' ? 'mode-active' : ''}`}
                onClick={() => setMode('real')}
              >🟢 Real Deploy</button>
            </div>

            {mode === 'real' && (
              <div className="token-wrap">
                <label className="field-label">🔑 {plan.token_name}</label>
                <input
                  type="password"
                  className="s-input"
                  value={token}
                  onChange={e => setToken(e.target.value)}
                  placeholder={`Paste your ${plan.token_name} here`}
                />
              </div>
            )}

            <button className="btn-deploy" onClick={deploy}>
              <Rocket size={20}/> Start Deployment
            </button>
          </div>

          {/* ── Token Guide (inline inside analysis card) ── */}
          <div className="tg-inline-wrap">
            <TokenGuide/>
          </div>
        </div>
      )}

      {/* ── Terminal Logs ── */}
      <div className="card glass term-card">
        <div className="term-bar">
          <div className="term-dots">
            <span className="tdot tdot-r"/><span className="tdot tdot-y"/><span className="tdot tdot-g"/>
          </div>
          <span className="term-name">deployment-logs — bash</span>
        </div>
        <pre className="term-body">{logs || '// Logs will appear here as the pipeline executes...'}</pre>
      </div>

      {/* ── Success ── */}
      {status === 'Success' && (
        <div className="result-card glass success-glow">
          <CheckCircle size={52} className="rc-icon rc-green"/>
          <h2 className="rc-title">Deployment Successful! 🎉</h2>

          {isSimulation && (
            <div className="alert-box alert-info">
              ⚠️ <strong>Simulation Mode</strong> — The URL below is a <em>fake/preview URL</em>.
              It does <strong>not</strong> point to a real hosted website.
              Switch to <strong>Real Deployment Mode</strong> and provide your platform token to get a live URL.
            </div>
          )}

          {liveUrl ? (
            <div className="url-card">
              <span className={`url-badge ${isSimulation ? 'ubadge-sim' : 'ubadge-live'}`}>
                {isSimulation ? '🔵 Simulation URL' : '🟢 Live URL'}
              </span>
              <div className="url-row">
                <code className="url-code">{liveUrl}</code>
                <CopyButton text={liveUrl}/>
              </div>
              {!isSimulation ? (
                <a href={liveUrl} target="_blank" rel="noreferrer" className="btn-open">
                  Open Live Website <ExternalLink size={16}/>
                </a>
              ) : (
                <p className="sim-note">⬆ This is a generated preview URL. Use Real Mode for an actual deployment.</p>
              )}
            </div>
          ) : (
            <p className="muted">Deployment completed but the platform did not return a URL.</p>
          )}
        </div>
      )}

      {/* ── Failed ── */}
      {status === 'Failed' && (
        <div className="result-card glass error-glow">
          <AlertTriangle size={52} className="rc-icon rc-red"/>
          <h2 className="rc-title">Deployment Failed</h2>
          <p className="muted">Check the terminal logs above for details and the suggested fix.</p>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App/>);
