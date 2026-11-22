const configuredApiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

export const API_BASE_URL = configuredApiUrl.replace(/\/+$/, '');

export function apiUrl(path) {
  return `${API_BASE_URL}/${path.replace(/^\/+/, '')}`;
}

export function resolveMediaUrl(path) {
  if (typeof path !== 'string' || !path) {
    return '';
  }
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  return `${API_BASE_URL}/${path.replace(/^\/+/, '')}`;
}

async function requestJson(path, options) {
  const response = await fetch(apiUrl(path), options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof data?.detail === 'string' ? data.detail : '';
    throw new Error(detail || `Request failed (${response.status}).`);
  }
  return data;
}

function expectArray(data, resource) {
  if (!Array.isArray(data)) {
    throw new Error(`The ${resource} response is not a list.`);
  }
  return data.filter((item) => item && typeof item === 'object' && !Array.isArray(item));
}

function normalizeComment(comment) {
  return {
    ...comment,
    author_handle: typeof comment.author_handle === 'string' ? comment.author_handle : 'community',
    text: typeof comment.text === 'string' ? comment.text : '',
  };
}

function normalizeCreator(creator) {
  return {
    ...creator,
    handle: typeof creator.handle === 'string' ? creator.handle : '',
    display_name: typeof creator.display_name === 'string' ? creator.display_name : '',
    niche: typeof creator.niche === 'string' ? creator.niche : '',
    avatar_url: typeof creator.avatar_url === 'string' ? creator.avatar_url : '',
    bio: typeof creator.bio === 'string' ? creator.bio : '',
  };
}

function normalizeContent(content) {
  const creator = content.creator && typeof content.creator === 'object' && !Array.isArray(content.creator)
    ? normalizeCreator(content.creator)
    : {};
  return {
    ...content,
    content_slug: typeof content.content_slug === 'string' ? content.content_slug : '',
    media_type: typeof content.media_type === 'string' ? content.media_type : 'post',
    thumbnail_path: typeof content.thumbnail_path === 'string' ? content.thumbnail_path : '',
    video_path: typeof content.video_path === 'string' ? content.video_path : null,
    caption: typeof content.caption === 'string' ? content.caption : '',
    likes: Number(content.likes) || 0,
    comments_count: Number(content.comments_count) || 0,
    creator,
    comments: Array.isArray(content.comments)
      ? content.comments
        .filter((comment) => comment && typeof comment === 'object' && !Array.isArray(comment))
        .map(normalizeComment)
      : [],
  };
}

function expectSession(data) {
  if (
    !data
    || typeof data !== 'object'
    || typeof data.access_token !== 'string'
    || typeof data.username !== 'string'
  ) {
    throw new Error('The authentication response is invalid.');
  }
  return data;
}

export function fetchFeed() {
  return requestJson('/api/sim/feed?demo_only=false&limit=500')
    .then((data) => expectArray(data, 'feed').map(normalizeContent));
}

export function fetchCreators(search = '') {
  const params = new URLSearchParams({ limit: '120' });
  if (typeof search === 'string' && search.trim()) {
    params.set('search', search.trim());
  }
  return requestJson(`/api/sim/creators?${params.toString()}`)
    .then((data) => expectArray(data, 'creator').map(normalizeCreator));
}

export function fetchCreatorProfile(handle) {
  if (typeof handle !== 'string' || !handle.trim()) {
    return Promise.reject(new Error('A creator handle is required.'));
  }
  return requestJson(`/api/sim/creators/${encodeURIComponent(handle)}`)
    .then((data) => {
      if (!data || typeof data !== 'object' || Array.isArray(data)) {
        throw new Error('The creator profile response is invalid.');
      }
      return {
        ...normalizeCreator(data),
        contents: Array.isArray(data.contents)
          ? data.contents
            .filter((content) => content && typeof content === 'object' && !Array.isArray(content))
            .map(normalizeContent)
          : [],
      };
    });
}

export function demoLogin(username, password) {
  return requestJson('/api/sim/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  }).then(expectSession);
}

export function demoRegister(username, email, password) {
  return requestJson('/api/sim/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email: email || null, password }),
  }).then(expectSession);
}
