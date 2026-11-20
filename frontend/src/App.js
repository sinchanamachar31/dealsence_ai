import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Fade, Modal } from '@mui/material';
import './App.css';
import ImageUpload from './ImageUpload';
import Icon from './Icon';
import Post from './Post';
import { apiUrl } from './api';

function Avatar({ name, size = 'regular', story = false }) {
  const initials = (name || '?').trim().slice(0, 1).toUpperCase();

  return (
    <span className={`avatar avatar--${size}${story ? ' avatar--story' : ''}`} aria-hidden="true">
      {initials}
    </span>
  );
}

function getErrorMessage(response, data) {
  if (data?.detail) {
    return typeof data.detail === 'string' ? data.detail : 'Please check the information and try again.';
  }
  return `Request failed (${response.status}). Please try again.`;
}

function App() {
  const [posts, setPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [feedError, setFeedError] = useState('');
  const [authMode, setAuthMode] = useState('');
  const [authError, setAuthError] = useState('');
  const [authBusy, setAuthBusy] = useState(false);
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [authToken, setAuthToken] = useState(() => window.localStorage.getItem('authToken'));
  const [authTokenType, setAuthTokenType] = useState(() => window.localStorage.getItem('authTokenType'));
  const [userId, setUserId] = useState(() => window.localStorage.getItem('userId'));
  const [username, setUsername] = useState(() => window.localStorage.getItem('username'));
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const composerRef = useRef(null);
  const searchRef = useRef(null);

  useEffect(() => {
    const storedValues = {
      authToken,
      authTokenType,
      userId,
      username,
    };

    Object.entries(storedValues).forEach(([key, value]) => {
      if (value) {
        window.localStorage.setItem(key, value);
      } else {
        window.localStorage.removeItem(key);
      }
    });
  }, [authToken, authTokenType, userId, username]);

  useEffect(() => {
    let isMounted = true;

    fetch(apiUrl('post/all'))
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) {
          throw new Error(getErrorMessage(response, data));
        }
        return data;
      })
      .then((data) => {
        if (isMounted) {
          setPosts(data);
          setFeedError('');
        }
      })
      .catch(() => {
        if (isMounted) {
          setFeedError('We couldn’t load the feed. Check that the backend is running, then try again.');
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const creators = useMemo(() => {
    const byUsername = new Map();
    posts.forEach((post) => {
      const creatorName = post.user?.username;
      if (creatorName && creatorName !== username && !byUsername.has(creatorName)) {
        byUsername.set(creatorName, post);
      }
    });
    return Array.from(byUsername.values()).slice(0, 5);
  }, [posts, username]);

  const visiblePosts = useMemo(() => {
    const query = searchQuery.trim().replace(/^@/, '').toLowerCase();
    if (!query) {
      return posts;
    }

    return posts.filter((post) => (
      post.user?.username?.toLowerCase().includes(query)
      || post.caption?.toLowerCase().includes(query)
      || post.post_title?.toLowerCase().includes(query)
    ));
  }, [posts, searchQuery]);

  const closeAuth = () => {
    setAuthMode('');
    setAuthError('');
    setPassword('');
  };

  const authenticate = async (loginName, loginPassword) => {
    const formData = new FormData();
    formData.append('username', loginName);
    formData.append('password', loginPassword);

    const response = await fetch(apiUrl('login'), {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(getErrorMessage(response, data));
    }

    setAuthToken(data.access_token);
    setAuthTokenType(data.token_type);
    setUserId(String(data.user_id));
    setUsername(data.username);
  };

  const signIn = async (event) => {
    event.preventDefault();
    setAuthBusy(true);
    setAuthError('');
    try {
      await authenticate(username, password);
      closeAuth();
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthBusy(false);
    }
  };

  const signUp = async (event) => {
    event.preventDefault();
    setAuthBusy(true);
    setAuthError('');
    try {
      const response = await fetch(apiUrl('user/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(getErrorMessage(response, data));
      }

      await authenticate(username, password);
      closeAuth();
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthBusy(false);
    }
  };

  const signOut = () => {
    setAuthToken(null);
    setAuthTokenType(null);
    setUserId('');
    setUsername('');
  };

  const openSearch = () => {
    setSearchOpen(true);
    window.setTimeout(() => searchRef.current?.focus(), 0);
  };

  const showComposer = () => {
    composerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  const updatePost = (createdPost) => {
    setPosts((currentPosts) => [createdPost, ...currentPosts]);
  };

  const removePost = (postId) => {
    setPosts((currentPosts) => currentPosts.filter((post) => post.id !== postId));
  };

  const switchAuthMode = (mode) => {
    setAuthMode(mode);
    setAuthError('');
  };

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Main navigation">
        <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Instagram home">
          <span className="brand-mark"><Icon name="instagram" /></span>
          <span className="brand-word">Instagram</span>
        </button>

        <nav className="sidebar-nav">
          <button className={`nav-item${searchOpen ? '' : ' nav-item--active'}`} aria-label="Home" onClick={() => { setSearchQuery(''); setSearchOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
            <Icon name="home" /><span>Home</span>
          </button>
          <button className={`nav-item${searchOpen ? ' nav-item--active' : ''}`} aria-label="Search" onClick={openSearch}>
            <Icon name="search" /><span>Search</span>
          </button>
          <button className="nav-item" aria-label="Explore" onClick={() => { setSearchQuery(''); setSearchOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
            <Icon name="compass" /><span>Explore</span>
          </button>
          <button className="nav-item" aria-label="Create" onClick={authToken ? showComposer : () => switchAuthMode('signin')}>
            <Icon name="plus" /><span>Create</span>
          </button>
          <button className="nav-item" aria-label={authToken ? 'Log out' : 'Log in'} onClick={() => authToken ? signOut() : switchAuthMode('signin')}>
            <Avatar name={username || 'you'} size="nav" />
            <span>{authToken ? 'Log out' : 'Log in'}</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <span className="sidebar-note">A little inspiration, every day.</span>
          <span className="sidebar-version">PHOTO SHARING · 2026</span>
        </div>
      </aside>

      <header className="mobile-header">
        <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Instagram home">
          <span className="brand-mark"><Icon name="instagram" /></span>
          <span className="brand-word">Instagram</span>
        </button>
        <div className="mobile-actions">
          <button className="icon-button" aria-label="Search posts" onClick={openSearch}><Icon name="search" /></button>
          {authToken
            ? <button className="text-button" onClick={signOut}>Log out</button>
            : <button className="text-button" onClick={() => switchAuthMode('signin')}>Log in</button>}
        </div>
      </header>

      <main className="main-layout">
        <section className="feed-column" aria-label="Feed">
          <div className="feed-heading">
            <div>
              <span className="eyebrow">YOUR LITTLE CORNER OF THE INTERNET</span>
              <h1>Good things, shared.</h1>
              <p>Catch up with your community and find a little inspiration.</p>
            </div>
            <span className="heading-sparkle" aria-hidden="true"><Icon name="sparkle" /></span>
          </div>

          {searchOpen && (
            <div className="search-panel">
              <Icon name="search" />
              <input
                ref={searchRef}
                type="search"
                placeholder="Search people or captions"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                aria-label="Search people or captions"
              />
              {searchQuery && (
                <button className="icon-button search-clear" onClick={() => setSearchQuery('')} aria-label="Clear search">
                  <Icon name="close" />
                </button>
              )}
              <button className="search-close" onClick={() => { setSearchOpen(false); setSearchQuery(''); }}>Done</button>
            </div>
          )}

          {authToken && (
            <div ref={composerRef} className="composer-anchor">
              <ImageUpload
                authToken={authToken}
                authTokenType={authTokenType}
                userId={userId}
                username={username}
                onPostCreated={updatePost}
              />
            </div>
          )}

          <div className="feed-section-heading">
            <div>
              <span className="eyebrow">THE COMMUNITY</span>
              <h2>{searchQuery ? 'Search results' : 'Your feed'}</h2>
            </div>
            {searchQuery && <span className="result-count">{visiblePosts.length} {visiblePosts.length === 1 ? 'post' : 'posts'}</span>}
          </div>

          {isLoading && (
            <div className="loading-list" aria-label="Loading posts">
              {[0, 1].map((item) => <div className="skeleton-post" key={item} />)}
            </div>
          )}

          {!isLoading && feedError && (
            <div className="empty-card error-card" role="alert">
              <span className="empty-icon"><Icon name="refresh" /></span>
              <h2>Feed taking a breather</h2>
              <p>{feedError}</p>
              <button className="primary-button" onClick={() => window.location.reload()}>Try again</button>
            </div>
          )}

          {!isLoading && !feedError && visiblePosts.length > 0 && (
            <div className="post-list">
              {visiblePosts.map((post, index) => (
                <Post
                  key={post.id}
                  post={post}
                  authToken={authToken}
                  authTokenType={authTokenType}
                  username={username}
                  canDelete={post.user?.username === username && Boolean(authToken)}
                  onDelete={removePost}
                  onLogin={() => switchAuthMode('signin')}
                  animationIndex={index}
                />
              ))}
            </div>
          )}

          {!isLoading && !feedError && visiblePosts.length === 0 && (
            <div className="empty-card">
              <span className="empty-icon"><Icon name={searchQuery ? 'search' : 'camera'} /></span>
              <span className="eyebrow">{searchQuery ? 'NOTHING HERE JUST YET' : 'A FRESH START'}</span>
              <h2>{searchQuery ? 'No moments found' : 'Your feed is ready for its first moment.'}</h2>
              <p>
                {searchQuery
                  ? 'Try another name or a different caption.'
                  : 'The best feeds start with one little hello. Share something you love, or come back when your community starts posting.'}
              </p>
              {searchQuery ? (
                <button className="primary-button" onClick={() => setSearchQuery('')}>Clear search</button>
              ) : authToken ? (
                <button className="primary-button" onClick={showComposer}>Share a moment</button>
              ) : (
                <button className="primary-button" onClick={() => switchAuthMode('signup')}>Join the community</button>
              )}
            </div>
          )}
        </section>

        <aside className="right-rail" aria-label="Your account and community">
          <section className="profile-card">
            <div className="profile-card-user">
              <Avatar name={username || 'you'} size="large" story={Boolean(authToken)} />
              <div className="profile-copy">
                <strong>{username || 'your.space'}</strong>
                <span>{authToken ? 'Welcome back' : 'Make yourself at home'}</span>
              </div>
            </div>
            {authToken ? (
              <button className="quiet-link" onClick={signOut}>Log out</button>
            ) : (
              <button className="quiet-link" onClick={() => switchAuthMode('signin')}>Log in</button>
            )}
          </section>

          <section className="community-card">
            <div className="rail-heading">
              <h2>People in your feed</h2>
              <span>COMMUNITY</span>
            </div>
            {creators.length > 0 ? (
              <div className="creator-list">
                {creators.map((creatorPost) => (
                  <button
                    className="creator-row"
                    key={creatorPost.user.username}
                    onClick={() => {
                      setSearchOpen(true);
                      setSearchQuery(`@${creatorPost.user.username}`);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                  >
                    <Avatar name={creatorPost.user.username} size="regular" story />
                    <span className="creator-copy">
                      <strong>{creatorPost.user.username}</strong>
                      <span>Sharing moments</span>
                    </span>
                    <span className="quiet-link">View</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="community-empty">
                <span className="community-empty-icon"><Icon name="users" /></span>
                <p>Your community will show up here as people start sharing.</p>
              </div>
            )}
          </section>

          <section className="inspiration-card">
            <span className="inspiration-icon"><Icon name="sparkle" /></span>
            <span className="eyebrow">A GENTLE REMINDER</span>
            <p>Little moments make lovely memories.</p>
          </section>

          <footer className="rail-footer">
            <span>About · Help · Privacy</span>
            <span>© 2026 INSTAGRAM COMMUNITY</span>
          </footer>
        </aside>
      </main>

      <nav className="mobile-nav" aria-label="Mobile navigation">
        <button className={`mobile-nav-item${searchOpen ? '' : ' mobile-nav-item--active'}`} onClick={() => { setSearchQuery(''); setSearchOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }} aria-label="Home">
          <Icon name="home" />
        </button>
        <button className="mobile-nav-item" onClick={openSearch} aria-label="Search"><Icon name="search" /></button>
        <button className="mobile-nav-item mobile-nav-create" onClick={authToken ? showComposer : () => switchAuthMode('signin')} aria-label="Create post">
          <Icon name="plus" />
        </button>
        <button className="mobile-nav-item" onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })} aria-label="Community">
          <Icon name="users" />
        </button>
        <button className="mobile-nav-item" onClick={authToken ? signOut : () => switchAuthMode('signin')} aria-label={authToken ? 'Log out' : 'Log in'}>
          <Avatar name={username || 'you'} size="nav" />
        </button>
      </nav>

      <Modal
        open={Boolean(authMode)}
        onClose={closeAuth}
        closeAfterTransition
        aria-labelledby="auth-title"
      >
        <Fade in={Boolean(authMode)}>
          <div className="auth-modal-shell">
            <section className="auth-card" role="dialog" aria-modal="true" aria-labelledby="auth-title">
              <button className="auth-close icon-button" onClick={closeAuth} aria-label="Close dialog">
                <Icon name="close" />
              </button>
              <div className="auth-brand-mark"><Icon name="instagram" /></div>
              <span className="eyebrow">{authMode === 'signup' ? 'COME ON IN' : 'GOOD TO SEE YOU'}</span>
              <h2 id="auth-title">{authMode === 'signup' ? 'Create your account' : 'Welcome back'}</h2>
              <p className="auth-description">
                {authMode === 'signup'
                  ? 'Join the community and start sharing your favorite moments.'
                  : 'Log in to catch up with your community.'}
              </p>
              <form className="auth-form" onSubmit={authMode === 'signup' ? signUp : signIn}>
                <label htmlFor="auth-username">Username</label>
                <input
                  id="auth-username"
                  type="text"
                  autoComplete="username"
                  value={username || ''}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                />
                {authMode === 'signup' && (
                  <>
                    <label htmlFor="auth-email">Email</label>
                    <input
                      id="auth-email"
                      type="email"
                      autoComplete="email"
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      required
                    />
                  </>
                )}
                <label htmlFor="auth-password">Password</label>
                <input
                  id="auth-password"
                  type="password"
                  autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
                {authError && <p className="auth-error" role="alert">{authError}</p>}
                <button className="primary-button auth-submit" type="submit" disabled={authBusy}>
                  {authBusy ? 'One moment…' : authMode === 'signup' ? 'Create account' : 'Log in'}
                </button>
              </form>
              <div className="auth-switch">
                <span>{authMode === 'signup' ? 'Already part of the community?' : 'New around here?'}</span>
                <button onClick={() => switchAuthMode(authMode === 'signup' ? 'signin' : 'signup')}>
                  {authMode === 'signup' ? 'Log in' : 'Create an account'}
                </button>
              </div>
            </section>
          </div>
        </Fade>
      </Modal>
    </div>
  );
}

export default App;
