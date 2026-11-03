let csrfToken = null;

async function ensureCsrf() {
  if (csrfToken) return csrfToken;
  const response = await fetch('/api/csrf', { credentials: 'same-origin' });
  if (!response.ok) throw new Error('Could not initialise secure session. Refresh and try again.');
  const payload = await response.json();
  csrfToken = payload.csrf_token;
  return csrfToken;
}

export async function api(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = { ...(options.headers || {}) };
  if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) headers['X-CSRFToken'] = await ensureCsrf();

  const response = await fetch('/api' + path, {
    ...options,
    method,
    headers,
    credentials: 'same-origin',
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || 'Request failed (' + response.status + ')');
  if (['/auth/register', '/auth/login', '/auth/logout'].includes(path)) csrfToken = null;
  return payload;
}

export async function streamMessage(conversationId, content, onDelta) {
  const token = await ensureCsrf();
  const response = await fetch('/api/conversations/' + conversationId + '/messages', {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.error || 'Request failed (' + response.status + ')');
  }
  if (!response.body) throw new Error('Streaming is not supported by this browser.');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const result = await reader.read();
    if (result.done) break;
    buffer += decoder.decode(result.value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';
    for (const eventText of events) {
      const line = eventText.split('\n').find(value => value.startsWith('data:'));
      if (!line) continue;
      const event = JSON.parse(line.slice(5).trim());
      if (event.type === 'delta') onDelta(event.content);
      if (event.type === 'error') throw new Error(event.error);
    }
  }
}
