import { useCallback, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ArrowUp, Bot, BookOpen, BriefcaseBusiness, Check, ChevronDown, Code2, FileCode2,
  FolderKanban, GraduationCap, LogOut, Menu, MessageSquare, Plus, Search, Settings2,
  ShieldCheck, Sparkles, Trash2, UserRound, X,
} from 'lucide-react';
import { api, streamMessage } from './api.js';

const prompts = [
  ['Teach me a concept', 'Teach me how Python functions work, with an example and a short exercise.'],
  ['Debug my project', 'Help me debug this project. First explain what information you need from me.'],
  ['Build a feature', 'Help me plan and implement a REST API endpoint with tests.'],
  ['Review my code', 'Review my code for correctness, security, and maintainability.'],
];

const modes = [
  { id: 'teach', label: 'Teach', hint: 'Explain concepts and guide my learning', Icon: GraduationCap },
  { id: 'build', label: 'Build', hint: 'Plan and implement software with me', Icon: Code2 },
  { id: 'review', label: 'Review', hint: 'Review code and find actionable issues', Icon: ShieldCheck },
];

function AuthScreen({ onSuccess }) {
  const [mode, setMode] = useState('signup');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const path = mode === 'signup' ? '/auth/register' : '/auth/login';
      const payload = mode === 'signup' ? { display_name: name, email, password } : { email, password };
      const result = await api(path, { method: 'POST', body: JSON.stringify(payload) });
      await onSuccess(result.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand"><span className="brand-icon"><Sparkles size={20} /></span><span>SkillForge <b>AI</b></span></div>
        <p className="eyebrow">BUILT IN NEPAL · MADE FOR EVERYONE</p>
        <h1>Your ideas deserve<br /><span>a thinking partner.</span></h1>
        <p className="muted">Learn technology, build real projects, and solve difficult problems with an AI mentor and development partner.</p>
        <form onSubmit={submit} className="auth-form">
          <div className="tabs">
            <button type="button" className={mode === 'signup' ? 'active' : ''} onClick={() => setMode('signup')}>Create account</button>
            <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Sign in</button>
          </div>
          {mode === 'signup' && <label>Name<input value={name} onChange={e => setName(e.target.value)} autoComplete="name" maxLength={100} required placeholder="Your name" /></label>}
          <label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} autoComplete="email" required placeholder="you@example.com" /></label>
          <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} minLength={mode === 'signup' ? 10 : 1} required placeholder={mode === 'signup' ? 'At least 10 characters' : 'Your password'} /></label>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={busy}>{busy ? 'Please wait…' : mode === 'signup' ? 'Create free account' : 'Sign in'} <ArrowUp size={17} /></button>
        </form>
        <p className="footnote">Prompts and selected project context are sent to the configured model provider. Avoid adding secrets or sensitive personal information.</p>
      </section>
      <aside className="auth-art"><div className="art-orb"><Sparkles size={56} /></div><h2>Learn deeply.<br />Build confidently.</h2><p>One partner for learning and making.</p><span>NEPAL 🇳🇵</span></aside>
    </main>
  );
}

function SourceList({ sources = [] }) {
  if (!sources.length) return null;
  return (
    <div className="source-list">
      <span className="source-heading"><BookOpen size={12} /> CONTEXT USED</span>
      {sources.map(source => (
        <span className={'source-chip ' + source.kind} key={source.id + source.label} title={source.label}>
          <b>[{source.id}]</b> {source.label}
        </span>
      ))}
    </div>
  );
}

function ProjectPanel({
  projects, selectedProjectId, onSelectProject, onClose, onCreateProject,
  onAddFile, onDeleteFile, profile, setProfile, onSaveProfile,
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [goals, setGoals] = useState('');
  const [stack, setStack] = useState('Python, Flask, React, MySQL');
  const [path, setPath] = useState('');
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const active = projects.find(item => String(item.id) === String(selectedProjectId));

  async function create(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const project = await onCreateProject({
        name, description, goals,
        tech_stack: stack.split(',').map(value => value.trim()).filter(Boolean),
      });
      setName('');
      setDescription('');
      setGoals('');
      onSelectProject(String(project.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function addFile(event) {
    event.preventDefault();
    if (!file || !active) return;
    setBusy(true);
    setError('');
    try {
      const content = await file.text();
      await onAddFile(active.id, path.trim() || file.name, content);
      setFile(null);
      setPath('');
      event.target.reset();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel-backdrop" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="project-panel" role="dialog" aria-modal="true" aria-labelledby="project-panel-title">
        <header className="panel-header">
          <div><span className="eyebrow">PERSONAL KNOWLEDGE</span><h2 id="project-panel-title">Your projects</h2></div>
          <button className="icon-btn" onClick={onClose} aria-label="Close project manager"><X size={19} /></button>
        </header>
        <p className="panel-intro">Add a project and selected source files. SkillForge retrieves relevant snippets when helping with that project. Files are stored as text and are never executed.</p>
        <label className="panel-label">Active project
          <select className="panel-input" value={selectedProjectId || ''} onChange={event => onSelectProject(event.target.value)}>
            <option value="">No project attached</option>
            {projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>
        </label>
        {active && (
          <div className="project-files">
            <div className="project-section-title"><FolderKanban size={15} /> {active.name} <span>{active.file_count} files</span></div>
            {active.files?.map(item => (
              <div className="file-row" key={item.id}>
                <FileCode2 size={14} /><span>{item.path}</span>
                <button className="icon-btn danger" title={'Remove ' + item.path} onClick={() => onDeleteFile(active.id, item.id)}><Trash2 size={14} /></button>
              </div>
            ))}
            {!active.files?.length && <p className="muted small">No source files added yet.</p>}
            <form className="panel-form" onSubmit={addFile}>
              <b>Add a source file</b>
              <label className="panel-label">Project path (optional)<input className="panel-input" value={path} onChange={event => setPath(event.target.value)} placeholder="backend/app.py" /></label>
              <input type="file" accept=".py,.pyi,.js,.jsx,.ts,.tsx,.html,.css,.scss,.json,.md,.txt,.sql,.yml,.yaml,.toml,.sh,.java,.go,.rs,.php,.rb,.c,.cpp,.h,.hpp,.cs,.kt,.swift,.dart,.vue,.svelte,.xml,.graphql,.prisma,.ini,.cfg" onChange={event => setFile(event.target.files?.[0] || null)} />
              <button className="secondary-button" type="submit" disabled={!file || busy}><Plus size={14} /> Add file to context</button>
            </form>
          </div>
        )}
        <form className="panel-form" onSubmit={create}>
          <div className="project-section-title"><Plus size={15} /> Create a project</div>
          <label className="panel-label">Project name<input className="panel-input" value={name} onChange={event => setName(event.target.value)} maxLength={120} required placeholder="My AI assistant" /></label>
          <label className="panel-label">What are you building?<textarea className="panel-input" rows={2} value={description} onChange={event => setDescription(event.target.value)} maxLength={3000} placeholder="A web application that…" /></label>
          <label className="panel-label">Project goals<textarea className="panel-input" rows={2} value={goals} onChange={event => setGoals(event.target.value)} maxLength={2000} placeholder="What should it achieve?" /></label>
          <label className="panel-label">Technology stack<input className="panel-input" value={stack} onChange={event => setStack(event.target.value)} placeholder="Python, React, MySQL" /></label>
          <button className="secondary-button" type="submit" disabled={busy || !name.trim()}><Plus size={14} /> Create project</button>
        </form>
        <div className="panel-divider" />
        <div className="project-section-title"><Settings2 size={15} /> Learning preferences</div>
        <div className="profile-grid">
          <label className="panel-label">Experience
            <select className="panel-input" value={profile.experience_level} onChange={event => setProfile(value => ({ ...value, experience_level: event.target.value }))}>
              <option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option>
            </select>
          </label>
          <label className="panel-label">Language
            <select className="panel-input" value={profile.preferred_language} onChange={event => setProfile(value => ({ ...value, preferred_language: event.target.value }))}>
              <option value="auto">Follow my message</option><option value="en">English</option><option value="ne">नेपाली</option>
            </select>
          </label>
          <label className="panel-label">Teaching style
            <select className="panel-input" value={profile.teaching_style} onChange={event => setProfile(value => ({ ...value, teaching_style: event.target.value }))}>
              <option value="step-by-step">Step by step</option><option value="concise">Concise</option><option value="socratic">Ask me questions</option><option value="hands-on">Hands on</option>
            </select>
          </label>
          <label className="panel-label">Learning goals<textarea className="panel-input" rows={2} maxLength={2000} value={profile.learning_goals} onChange={event => setProfile(value => ({ ...value, learning_goals: event.target.value }))} placeholder="Learn Python, build AI products…" /></label>
        </div>
        {error && <div className="error">{error}</div>}
        <button className="secondary-button full" onClick={onSaveProfile}><Check size={14} /> Save learning preferences</button>
        <p className="footnote">Private project files and learning preferences are associated with your account. Do not upload credentials, tokens, production secrets, or private customer data.</p>
      </section>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mode, setMode] = useState('teach');
  const [projects, setProjects] = useState([]);
  const [projectId, setProjectId] = useState('');
  const [panelOpen, setPanelOpen] = useState(false);
  const [profile, setProfile] = useState({
    experience_level: 'beginner', preferred_language: 'auto',
    learning_goals: '', teaching_style: 'step-by-step',
  });
  const inputRef = useRef(null);
  const bottomRef = useRef(null);

  const loadConversations = useCallback(async () => {
    const result = await api('/conversations');
    setConversations(result.conversations || []);
    return result.conversations || [];
  }, []);

  const loadProjects = useCallback(async () => {
    const result = await api('/projects');
    const summaries = result.projects || [];
    const details = await Promise.all(summaries.map(item => api('/projects/' + item.id)));
    const full = details.map(item => item.project);
    setProjects(full);
    return full;
  }, []);

  const loadProfile = useCallback(async () => {
    const result = await api('/profile');
    if (result.profile) setProfile(result.profile);
  }, []);

  const loadWorkspace = useCallback(async () => {
    const [rows] = await Promise.all([loadConversations(), loadProjects(), loadProfile()]);
    if (rows.length) {
      const detail = await api('/conversations/' + rows[0].id);
      setActiveId(rows[0].id);
      setMessages(detail.messages || []);
      setMode(detail.conversation?.workspace?.mode || 'teach');
      setProjectId(detail.conversation?.workspace?.project_id ? String(detail.conversation.workspace.project_id) : '');
    }
  }, [loadConversations, loadProjects, loadProfile]);

  useEffect(() => {
    api('/auth/me')
      .then(async result => {
        if (!result.user) return;
        setUser(result.user);
        await loadWorkspace();
      })
      .catch(() => {})
      .finally(() => setChecking(false));
  }, [loadWorkspace]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  async function handleAuth(nextUser) {
    setUser(nextUser);
    await Promise.all([loadConversations(), loadProjects(), loadProfile()]);
  }

  async function chooseConversation(id) {
    setError('');
    setSidebarOpen(false);
    try {
      const detail = await api('/conversations/' + id);
      setActiveId(id);
      setMessages(detail.messages || []);
      setMode(detail.conversation?.workspace?.mode || 'teach');
      setProjectId(detail.conversation?.workspace?.project_id ? String(detail.conversation.workspace.project_id) : '');
    } catch (err) {
      setError(err.message);
    }
  }

  function newChat() {
    setActiveId(null);
    setMessages([]);
    setInput('');
    setError('');
    setSidebarOpen(false);
    inputRef.current?.focus();
  }

  async function deleteConversation() {
    if (!activeId) return;
    try {
      await api('/conversations/' + activeId, { method: 'DELETE' });
      const next = conversations.filter(item => item.id !== activeId);
      setConversations(next);
      setActiveId(null);
      setMessages([]);
      if (next.length) await chooseConversation(next[0].id);
    } catch (err) {
      setError(err.message);
    }
  }

  async function send(text = input) {
    const content = text.trim();
    if (!content || sending) return;
    setInput('');
    setError('');
    setSending(true);
    let conversationId = activeId;
    const userMessage = { id: 'local-user-' + Date.now(), role: 'user', content };
    const assistantId = 'local-assistant-' + Date.now();
    setMessages(current => [...current, userMessage, { id: assistantId, role: 'assistant', content: '', sources: [] }]);
    try {
      if (!conversationId) {
        const created = await api('/conversations', { method: 'POST', body: JSON.stringify({}) });
        conversationId = created.conversation.id;
        setActiveId(conversationId);
      }
      await streamMessage(
        conversationId,
        content,
        { mode, projectId },
        delta => setMessages(current => current.map(item => item.id === assistantId ? { ...item, content: item.content + delta } : item)),
        sources => setMessages(current => current.map(item => item.id === assistantId ? { ...item, sources } : item)),
      );
      await loadConversations();
      const detail = await api('/conversations/' + conversationId);
      setMessages(detail.messages || []);
    } catch (err) {
      setError(err.message);
      setMessages(current => current.filter(item => item.id !== assistantId));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }

  async function createProject(payload) {
    const result = await api('/projects', { method: 'POST', body: JSON.stringify(payload) });
    const full = await api('/projects/' + result.project.id);
    setProjects(current => [...current, full.project]);
    return full.project;
  }

  async function addProjectFile(id, path, content) {
    await api('/projects/' + id + '/files', {
      method: 'POST', body: JSON.stringify({ path, content }),
    });
    const result = await api('/projects/' + id);
    setProjects(current => current.map(item => item.id === id ? result.project : item));
  }

  async function deleteProjectFile(id, fileId) {
    await api('/projects/' + id + '/files/' + fileId, { method: 'DELETE' });
    const result = await api('/projects/' + id);
    setProjects(current => current.map(item => item.id === id ? result.project : item));
  }

  async function saveProfile() {
    try {
      const result = await api('/profile', { method: 'PUT', body: JSON.stringify(profile) });
      setProfile(result.profile);
      setError('');
      setPanelOpen(false);
    } catch (err) {
      setError(err.message);
    }
  }

  async function logout() {
    try {
      await api('/auth/logout', { method: 'POST', body: JSON.stringify({}) });
    } catch {}
    setUser(null);
    setConversations([]);
    setProjects([]);
    setActiveId(null);
    setMessages([]);
    setProjectId('');
  }

  if (checking) return <div className="loading"><Sparkles size={28} /> Preparing your workspace…</div>;
  if (!user) return <AuthScreen onSuccess={handleAuth} />;

  const activeProject = projects.find(item => String(item.id) === String(projectId));

  return (
    <div className="app-shell">
      {sidebarOpen && <button className="scrim" aria-label="Close sidebar" onClick={() => setSidebarOpen(false)} />}
      <aside className={'sidebar ' + (sidebarOpen ? 'open' : '')}>
        <div className="brand"><span className="brand-icon"><Sparkles size={18} /></span><span>SkillForge <b>AI</b></span></div>
        <button className="new-chat" onClick={newChat}><Plus size={17} /> New chat</button>
        <button className="manage-projects" onClick={() => setPanelOpen(true)}><FolderKanban size={15} /> My project knowledge <span>{projects.length}</span></button>
        <p className="section-label">RECENT CHATS</p>
        <nav className="history">
          {conversations.map(item => <button key={item.id} className={activeId === item.id ? 'history-item selected' : 'history-item'} onClick={() => chooseConversation(item.id)}><MessageSquare size={15} /><span>{item.title}</span></button>)}
          {!conversations.length && <p className="muted small">Your conversations will appear here.</p>}
        </nav>
        <div className="sidebar-bottom">
          <div className="free-tag"><Sparkles size={15} /> Free workspace · Nepal</div>
          <div className="account"><span className="avatar">{(user.display_name || 'U').slice(0, 1).toUpperCase()}</span><span className="account-text"><b>{user.display_name}</b><small>{user.email}</small></span><button className="icon-btn" title="Sign out" onClick={logout}><LogOut size={16} /></button></div>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <button className="icon-btn mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open menu"><Menu size={19} /></button>
          <div className="model-name"><Sparkles size={15} /> SkillForge AI <span>BETA</span></div>
          <div className="top-actions"><span className="online-dot" /> Personal workspace {activeId && <button className="icon-btn" title="Delete conversation" onClick={deleteConversation}><Trash2 size={16} /></button>}</div>
        </header>
        <div className="assistant-toolbar">
          <div className="mode-switch" role="group" aria-label="Assistant mode">
            {modes.map(item => <button key={item.id} className={mode === item.id ? 'active' : ''} title={item.hint} onClick={() => setMode(item.id)}><item.Icon size={14} /><span>{item.label}</span></button>)}
          </div>
          <div className="project-select-wrap">
            <FolderKanban size={14} />
            <select aria-label="Project context" value={projectId} onChange={event => setProjectId(event.target.value)}>
              <option value="">No project context</option>
              {projects.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <button className="manage-inline" onClick={() => setPanelOpen(true)}>Manage</button>
          </div>
          {activeProject && <div className="context-indicator"><Check size={12} /> {activeProject.file_count} project files available</div>}
        </div>
        <section className="chat-area">
          {!messages.length ? (
            <div className="welcome">
              <div className="welcome-mark"><Bot size={30} /></div>
              <p className="eyebrow">YOUR AI TEACHER & DEVELOPMENT PARTNER</p>
              <h1>What are we<br /><span>learning or building?</span></h1>
              <p className="muted intro">Choose Teach, Build or Review. Attach a project so SkillForge can use your selected source files and shared technical guides.</p>
              <div className="prompt-grid">
                {prompts.map(([title, text]) => <button key={title} className="prompt-card" onClick={() => send(text)}><b>{title}</b><span>{text}</span></button>)}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map(item => <article key={item.id} className={'message ' + item.role}><div className="message-icon">{item.role === 'assistant' ? <Sparkles size={16} /> : <UserRound size={16} />}</div><div className="message-content"><b>{item.role === 'assistant' ? 'SkillForge AI' : 'You'}</b><div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]}>{item.content || ''}</ReactMarkdown></div>{item.role === 'assistant' && <SourceList sources={item.sources} />}{sending && item.role === 'assistant' && !item.content && <span className="typing">Thinking…</span>}</div></article>)}
              <div ref={bottomRef} />
            </div>
          )}
        </section>
        <div className="composer-wrap">
          {error && <div className="error inline">{error}<button onClick={() => setError('')}><X size={14} /></button></div>}
          <form className="composer" onSubmit={event => { event.preventDefault(); send(); }}>
            <textarea ref={inputRef} rows={1} value={input} maxLength={12000} placeholder={mode === 'teach' ? 'Ask SkillForge to teach you something…' : mode === 'build' ? 'Describe the feature or bug you are working on…' : 'Paste code or describe what you want reviewed…'} onChange={event => setInput(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }} />
            <button className="send" type="submit" disabled={!input.trim() || sending} aria-label="Send message">{sending ? '…' : <ArrowUp size={19} />}</button>
          </form>
          <p className="disclaimer">Project context is private to your account. AI can make mistakes; verify important changes. · Built in Nepal 🇳🇵</p>
        </div>
      </main>
      {panelOpen && <ProjectPanel
        projects={projects}
        selectedProjectId={projectId}
        onSelectProject={setProjectId}
        onClose={() => setPanelOpen(false)}
        onCreateProject={createProject}
        onAddFile={addProjectFile}
        onDeleteFile={deleteProjectFile}
        profile={profile}
        setProfile={setProfile}
        onSaveProfile={saveProfile}
      />}
    </div>
  );
}
