import { useCallback, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowUp, Bot, LogOut, Menu, MessageSquare, Plus, Sparkles, Trash2, UserRound, X } from 'lucide-react';
import { api, streamMessage } from './api.js';

const prompts = [
  ['Explain a concept', 'Explain how large language models work in simple terms.'],
  ['Help me code', 'Help me build a REST API with Python Flask.'],
  ['Write something', 'Help me write a professional project proposal.'],
  ['Ask in Nepali', 'मलाई कृत्रिम बुद्धिमत्ता के हो भनेर सजिलो भाषामा बुझाउनुहोस्।'],
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
      onSuccess(result.user);
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
        <p className="muted">Ask questions, explore ideas, write, code and solve problems with SkillForge AI.</p>
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
        <p className="footnote">Your prompts are sent to the AI provider configured by this service. Avoid sharing sensitive information.</p>
      </section>
      <aside className="auth-art"><div className="art-orb"><Sparkles size={56} /></div><h2>Think clearly.<br />Create boldly.</h2><p>One space. Many possibilities.</p><span>NEPAL 🇳🇵</span></aside>
    </main>
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
  const inputRef = useRef(null);
  const bottomRef = useRef(null);

  const loadConversations = useCallback(async () => {
    const result = await api('/conversations');
    setConversations(result.conversations || []);
    return result.conversations || [];
  }, []);

  useEffect(() => {
    api('/auth/me')
      .then(async result => {
        if (!result.user) return;
        setUser(result.user);
        const rows = await loadConversations();
        if (rows.length) {
          setActiveId(rows[0].id);
          const detail = await api('/conversations/' + rows[0].id);
          setMessages(detail.messages || []);
        }
      })
      .catch(() => {})
      .finally(() => setChecking(false));
  }, [loadConversations]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  async function chooseConversation(id) {
    setError('');
    setSidebarOpen(false);
    try {
      const detail = await api('/conversations/' + id);
      setActiveId(id);
      setMessages(detail.messages || []);
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
    setMessages(current => [...current, userMessage, { id: assistantId, role: 'assistant', content: '' }]);
    try {
      if (!conversationId) {
        const created = await api('/conversations', { method: 'POST', body: JSON.stringify({}) });
        conversationId = created.conversation.id;
        setActiveId(conversationId);
      }
      await streamMessage(
        conversationId,
        content,
        delta => setMessages(current => current.map(item => item.id === assistantId ? { ...item, content: item.content + delta } : item)),
      );
      await loadConversations();
    } catch (err) {
      setError(err.message);
      setMessages(current => current.filter(item => item.id !== assistantId));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }

  async function logout() {
    try {
      await api('/auth/logout', { method: 'POST', body: JSON.stringify({}) });
    } catch {}
    setUser(null);
    setConversations([]);
    setActiveId(null);
    setMessages([]);
  }

  if (checking) return <div className="loading"><Sparkles size={28} /> Preparing your workspace…</div>;
  if (!user) return <AuthScreen onSuccess={async nextUser => { setUser(nextUser); await loadConversations(); }} />;

  return (
    <div className="app-shell">
      {sidebarOpen && <button className="scrim" aria-label="Close sidebar" onClick={() => setSidebarOpen(false)} />}
      <aside className={'sidebar ' + (sidebarOpen ? 'open' : '')}>
        <div className="brand"><span className="brand-icon"><Sparkles size={18} /></span><span>SkillForge <b>AI</b></span></div>
        <button className="new-chat" onClick={newChat}><Plus size={17} /> New chat</button>
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
        <section className="chat-area">
          {!messages.length ? (
            <div className="welcome">
              <div className="welcome-mark"><Bot size={30} /></div>
              <p className="eyebrow">YOUR AI THINKING PARTNER</p>
              <h1>What can we<br /><span>work on today?</span></h1>
              <p className="muted intro">Learn something new, solve a problem, write, research or build a project.</p>
              <div className="prompt-grid">
                {prompts.map(([title, text]) => <button key={title} className="prompt-card" onClick={() => send(text)}><b>{title}</b><span>{text}</span></button>)}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map(item => <article key={item.id} className={'message ' + item.role}><div className="message-icon">{item.role === 'assistant' ? <Sparkles size={16} /> : <UserRound size={16} />}</div><div className="message-content"><b>{item.role === 'assistant' ? 'SkillForge AI' : 'You'}</b><div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]}>{item.content || ''}</ReactMarkdown></div>{sending && item.role === 'assistant' && !item.content && <span className="typing">Thinking…</span>}</div></article>)}
              <div ref={bottomRef} />
            </div>
          )}
        </section>
        <div className="composer-wrap">
          {error && <div className="error inline">{error}<button onClick={() => setError('')}><X size={14} /></button></div>}
          <form className="composer" onSubmit={event => { event.preventDefault(); send(); }}>
            <textarea ref={inputRef} rows={1} value={input} maxLength={12000} placeholder="Message SkillForge AI…" onChange={event => setInput(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }} />
            <button className="send" type="submit" disabled={!input.trim() || sending} aria-label="Send message">{sending ? '…' : <ArrowUp size={19} />}</button>
          </form>
          <p className="disclaimer">SkillForge AI can make mistakes. Verify important information. · Built in Nepal 🇳🇵</p>
        </div>
      </main>
    </div>
  );
}
