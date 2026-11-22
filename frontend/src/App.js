import React, { useEffect, useMemo, useState } from 'react';
import { Modal } from '@mui/material';
import './App.css';
import Post from './Post';
import {
  demoLogin,
  demoRegister,
  fetchCreatorProfile,
  fetchCreators,
  fetchFeed,
  resolveMediaUrl,
} from './api';

const SPOTLIGHT_HANDLES = [
  '@ananya.nourish',
  '@meera.glowlab',
  '@rohan.movewell',
  '@kabir.desksetup',
  '@tara.earthhome',
];

function CreatorAvatar({ creator = {}, size = 'medium', story = false }) {
  const safeCreator = creator && typeof creator === 'object' ? creator : {};
  const label = [safeCreator.display_name, safeCreator.handle]
    .find((value) => typeof value === 'string' && value.trim()) || 'Creator';
  return (
    <span className={`creator-avatar creator-avatar--${size}${story ? ' creator-avatar--story' : ''}`}>
      {safeCreator.avatar_url
        ? <img src={resolveMediaUrl(safeCreator.avatar_url)} alt="" />
        : label.trim().slice(0, 1).toUpperCase()}
    </span>
  );
}

function formatCount(value = 0) {
  const count = Number(value) || 0;
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(count >= 10000000 ? 0 : 1).replace(/\.0$/, '')}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(count >= 10000 ? 0 : 1).replace(/\.0$/, '')}K`;
  }
  return String(count);
}

function App() {
  const [feed, setFeed] = useState([]);
  const [creators, setCreators] = useState([]);
  const [searchCreators, setSearchCreators] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentView, setCurrentView] = useState('home');
  const [selectedCreator, setSelectedCreator] = useState(null);
  const [profileTab, setProfileTab] = useState('all');
  const [theaterItem, setTheaterItem] = useState(null);
  const [likedItems, setLikedItems] = useState({});
  const [following, setFollowing] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [feedError, setFeedError] = useState('');
  const [creatorError, setCreatorError] = useState('');
  const [profileError, setProfileError] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [authMode, setAuthMode] = useState('');
  const [authError, setAuthError] = useState('');
  const [authBusy, setAuthBusy] = useState(false);
  const [authUsername, setAuthUsername] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authToken, setAuthToken] = useState(() => window.localStorage.getItem('authToken') || '');
  const [username, setUsername] = useState(() => window.localStorage.getItem('username') || '');
  const [displayName, setDisplayName] = useState(() => window.localStorage.getItem('displayName') || '');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    Promise.allSettled([fetchFeed(), fetchCreators()])
      .then(([feedResult, creatorResult]) => {
        if (!active) {
          return;
        }
        if (feedResult.status === 'fulfilled') {
          setFeed(feedResult.value);
          setFeedError('');
        } else {
          setFeedError('The feed could not be loaded. Check the API connection and try again.');
        }
        if (creatorResult.status === 'fulfilled') {
          setCreators(creatorResult.value);
          setCreatorError('');
        } else {
          setCreatorError('Creator directory is unavailable right now.');
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  useEffect(() => {
    const query = searchQuery.trim();
    if (!query) {
      setSearchCreators([]);
      setSearchLoading(false);
      return undefined;
    }

    let active = true;
    setSearchLoading(true);
    const timer = window.setTimeout(() => {
      fetchCreators(query)
        .then((results) => {
          if (active) {
            setSearchCreators(results);
          }
        })
        .catch(() => {
          if (active) {
            setSearchCreators([]);
          }
        })
        .finally(() => {
          if (active) {
            setSearchLoading(false);
          }
        });
    }, 220);

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [searchQuery]);

  const spotlightCreators = useMemo(
    () => SPOTLIGHT_HANDLES
      .map((handle) => creators.find((creator) => creator.handle === handle))
      .filter(Boolean),
    [creators],
  );

  const matchingPosts = useMemo(() => {
    const query = searchQuery.trim().replace(/^@/, '').toLowerCase();
    if (!query) {
      return [];
    }
    const containsQuery = (value) => typeof value === 'string' && value.toLowerCase().includes(query);
    return feed.filter((post) => post && (
      containsQuery(post.creator?.handle)
      || containsQuery(post.creator?.display_name)
      || containsQuery(post.creator?.niche)
      || containsQuery(post.caption)
      || containsQuery(post.content_slug)
    )).slice(0, 5);
  }, [feed, searchQuery]);

  const profilePosts = useMemo(() => {
    const contents = Array.isArray(selectedCreator?.contents)
      ? selectedCreator.contents.filter((content) => content && typeof content === 'object')
      : [];
    if (profileTab === 'reels') {
      return contents.filter((content) => Boolean(content.video_path));
    }
    return contents;
  }, [selectedCreator, profileTab]);

  const signOut = () => {
    window.localStorage.removeItem('authToken');
    window.localStorage.removeItem('username');
    window.localStorage.removeItem('displayName');
    setAuthToken('');
    setUsername('');
    setDisplayName('');
  };

  const openAuth = (mode = 'login') => {
    setAuthMode(mode);
    setAuthError('');
  };

  const closeAuth = () => {
    setAuthMode('');
    setAuthError('');
    setAuthPassword('');
  };

  const saveSession = (session) => {
    setAuthToken(session.access_token);
    setUsername(session.username);
    setDisplayName(session.display_name || session.username);
    window.localStorage.setItem('authToken', session.access_token);
    window.localStorage.setItem('username', session.username);
    window.localStorage.setItem('displayName', session.display_name || session.username);
    closeAuth();
  };

  const submitAuth = async (event) => {
    event.preventDefault();
    setAuthBusy(true);
    setAuthError('');
    try {
      const session = authMode === 'register'
        ? await demoRegister(authUsername, authEmail, authPassword)
        : await demoLogin(authUsername, authPassword);
      saveSession(session);
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthBusy(false);
    }
  };

  const quickDemoSignIn = async () => {
    setAuthBusy(true);
    setAuthError('');
    try {
      const session = await demoLogin('demo.viewer', 'demo123');
      saveSession(session);
    } catch (error) {
      setAuthError(error.message);
      setAuthMode('login');
    } finally {
      setAuthBusy(false);
    }
  };

  const openCreator = async (creatorOrHandle) => {
    const handle = typeof creatorOrHandle === 'string'
      ? creatorOrHandle
      : creatorOrHandle?.handle;
    if (!handle) {
      return;
    }
    setCurrentView('profile');
    setSelectedCreator(null);
    setProfileError('');
    setProfileTab('all');
    try {
      setSelectedCreator(await fetchCreatorProfile(handle));
    } catch (error) {
      const knownCreator = creators.find((creator) => creator.handle === handle);
      setProfileError(error.message || 'This profile could not be loaded.');
      if (knownCreator) {
        setSelectedCreator({
          ...knownCreator,
          contents: feed
            .filter((post) => post.creator?.handle === handle)
            .map(({ creator, ...content }) => content),
        });
      }
    }
  };

  const openTheater = (content, creator) => {
    if (!content || typeof content !== 'object' || Array.isArray(content)) {
      return;
    }
    const suppliedCreator = creator && typeof creator === 'object' && !Array.isArray(creator)
      ? creator
      : null;
    const contentCreator = content.creator && typeof content.creator === 'object' && !Array.isArray(content.creator)
      ? content.creator
      : {};
    const contentHasCreator = Object.keys(contentCreator).length > 0;
    setTheaterItem({
      ...content,
      creator: suppliedCreator || (contentHasCreator ? contentCreator : selectedCreator) || {},
      comments: Array.isArray(content.comments)
        ? content.comments.filter((comment) => comment && typeof comment === 'object' && !Array.isArray(comment))
        : [],
    });
  };

  const toggleLike = (content) => {
    const key = content.content_slug || content.id;
    if (key == null) {
      return;
    }
    setLikedItems((current) => ({ ...current, [key]: !current[key] }));
  };

  const showHome = () => {
    setCurrentView('home');
    setSelectedCreator(null);
    setSearchQuery('');
  };

  const openExplore = () => {
    setCurrentView('explore');
    setSelectedCreator(null);
  };

  const filteredDirectory = useMemo(() => {
    const query = searchQuery.trim().replace(/^@/, '').toLowerCase();
    const safeCreators = Array.isArray(creators)
      ? creators.filter((creator) => creator && typeof creator === 'object')
      : [];
    if (!query) return safeCreators;
    return safeCreators.filter((creator) => (
      (typeof creator.handle === 'string' && creator.handle.toLowerCase().includes(query))
      || (typeof creator.display_name === 'string' && creator.display_name.toLowerCase().includes(query))
      || (typeof creator.niche === 'string' && creator.niche.toLowerCase().includes(query))
    ));
  }, [creators, searchQuery]);

  return (
    <div className="sim-app">
      <header className="sim-topbar">
        <button className="sim-brand" onClick={showHome} aria-label="Go to home feed">
          <span className="sim-brand-mark">◎</span>
          <span>Instagram</span>
        </button>

        <nav className="sim-primary-nav" aria-label="Main navigation">
          <button
            className={currentView === 'home' ? 'is-active' : ''}
            onClick={showHome}
          >
            Home Feed
          </button>
          <button
            className={currentView === 'explore' ? 'is-active' : ''}
            onClick={openExplore}
          >
            Explore 100 Creators
          </button>
        </nav>

        <div className="sim-global-search">
          <span aria-hidden="true">⌕</span>
          <input
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search creators and posts"
            aria-label="Search all creators and posts"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} aria-label="Clear search">×</button>
          )}
          {searchQuery.trim() && (
            <div className="sim-search-popover">
              <div className="sim-search-group">
                <span className="sim-search-label">CREATORS</span>
                {searchLoading && <span className="sim-search-empty">Searching all creators...</span>}
                {!searchLoading && searchCreators.length === 0 && (
                  <span className="sim-search-empty">No matching creators</span>
                )}
                {searchCreators.slice(0, 5).map((creator) => (
                  <button
                    className="sim-search-result"
                    key={creator.id || creator.handle}
                    onClick={() => { setSearchQuery(''); openCreator(creator.handle); }}
                  >
                    <CreatorAvatar creator={creator} size="small" />
                    <span><strong>{creator.handle}</strong><small>{creator.niche}</small></span>
                  </button>
                ))}
              </div>
              <div className="sim-search-group">
                <span className="sim-search-label">POSTS & REELS</span>
                {matchingPosts.length === 0 && (
                  <span className="sim-search-empty">No matching posts</span>
                )}
                {matchingPosts.map((post) => (
                  <button
                    className="sim-search-result"
                    key={post.content_slug}
                    onClick={() => { setSearchQuery(''); openTheater(post); }}
                  >
                    <img src={resolveMediaUrl(post.thumbnail_path) || undefined} alt="" />
                    <span>
                      <strong>{post.creator?.handle || 'Creator'}</strong>
                      <small>{post.caption}</small>
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="sim-account-actions">
          {authToken ? (
            <>
              <span className="sim-signed-in">Hi, {displayName || username}</span>
              <button className="sim-button sim-button--quiet" onClick={signOut}>Sign out</button>
            </>
          ) : (
            <>
              <button className="sim-button sim-button--quiet" onClick={() => openAuth('login')}>
                Demo User Login
              </button>
              <button className="sim-button sim-button--primary" onClick={quickDemoSignIn} disabled={authBusy}>
                {authBusy ? 'Signing in...' : 'Quick Demo Sign-In'}
              </button>
            </>
          )}
        </div>
      </header>

      <main className="sim-main">
        {currentView === 'home' && (
          <>
            <section className="sim-welcome">
              <div>
                <span className="sim-eyebrow">YOUR CREATOR COMMUNITY</span>
                <h1>Good things, shared.</h1>
                <p>Discover thoughtful ideas, makers, and everyday inspiration.</p>
              </div>
              <button className="sim-welcome-link" onClick={openExplore}>
                Meet all 100 creators <span>→</span>
              </button>
            </section>

            <section className="sim-spotlight-section" aria-label="Spotlight creators">
              <div className="sim-section-heading">
                <div>
                  <span className="sim-eyebrow">CURATED FOR YOU</span>
                  <h2>Spotlight Creators</h2>
                </div>
                <button className="sim-text-link" onClick={openExplore}>Explore all 100 →</button>
              </div>
              <div className="sim-spotlight-strip">
                {spotlightCreators.map((creator) => (
                  <button
                    className="sim-spotlight-card"
                    key={creator.handle}
                    onClick={() => openCreator(creator.handle)}
                  >
                    <CreatorAvatar creator={creator} size="large" story />
                    <strong>{creator.handle}</strong>
                    <span>{creator.niche}</span>
                  </button>
                ))}
                {spotlightCreators.length === 0 && !creatorError && (
                  <p className="sim-muted">Loading spotlight creators...</p>
                )}
                {creatorError && <p className="sim-muted">{creatorError}</p>}
              </div>
            </section>

            <section className="sim-feed-section" aria-label="Home feed">
              <div className="sim-section-heading">
                <div>
                  <span className="sim-eyebrow">LATEST FROM THE COMMUNITY</span>
                  <h2>Home Feed</h2>
                </div>
                <span className="sim-feed-count">{feed.length} posts & reels</span>
              </div>

              {isLoading && <div className="sim-loading">Loading your feed...</div>}
              {!isLoading && feedError && (
                <div className="sim-empty-state" role="alert">
                  <h3>Feed taking a breather</h3>
                  <p>{feedError}</p>
                  <button className="sim-button sim-button--primary" onClick={() => setReloadKey((key) => key + 1)}>
                    Try again
                  </button>
                </div>
              )}
              {!isLoading && !feedError && feed.length === 0 && (
                <div className="sim-empty-state">
                  <h3>No posts yet</h3>
                  <p>Seed the simulation database to fill the community feed.</p>
                </div>
              )}
              {!isLoading && !feedError && feed.length > 0 && (
                <div className="sim-feed-grid">
                  {feed.map((post, index) => (
                    <Post
                      key={post.content_slug}
                      post={post}
                      animationIndex={index}
                      onCreatorClick={openCreator}
                      onOpenTheater={(item) => openTheater(item)}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}

        {currentView === 'explore' && (
          <section className="sim-directory">
            <div className="sim-page-heading">
              <span className="sim-eyebrow">FIND YOUR NEXT FOLLOW</span>
              <h1>Explore 100 Creators</h1>
              <p>Browse every creator across food, beauty, fitness, tech, and thoughtful home living.</p>
            </div>
            {creatorError && <div className="sim-empty-state">{creatorError}</div>}
            <div className="sim-directory-grid">
              {filteredDirectory.map((creator) => (
                <article className="sim-creator-card" key={creator.handle}>
                  <button className="sim-creator-card-main" onClick={() => openCreator(creator.handle)}>
                    <CreatorAvatar creator={creator} size="large" story={SPOTLIGHT_HANDLES.includes(creator.handle)} />
                    <span className="sim-creator-card-name">
                      <strong>{creator.handle}</strong>
                      <small>{creator.display_name}</small>
                    </span>
                    {SPOTLIGHT_HANDLES.includes(creator.handle) && (
                      <span className="sim-spotlight-badge">SPOTLIGHT</span>
                    )}
                    <span className="sim-creator-card-niche">{creator.niche}</span>
                    <span className="sim-creator-card-followers">{formatCount(creator.follower_count)} followers</span>
                  </button>
                  <button className="sim-button sim-button--outline" onClick={() => openCreator(creator.handle)}>
                    View profile
                  </button>
                </article>
              ))}
            </div>
            {!creatorError && filteredDirectory.length === 0 && (
              <div className="sim-empty-state">
                <h3>No creators found</h3>
                <p>Try a different search term.</p>
              </div>
            )}
          </section>
        )}

        {currentView === 'profile' && (
          <section className="sim-profile-view">
            <button className="sim-back-link" onClick={() => setCurrentView('explore')}>
              ← Back to creators
            </button>
            {profileError && <p className="sim-inline-error">{profileError}</p>}
            {!selectedCreator && !profileError && <div className="sim-loading">Loading creator profile...</div>}
            {selectedCreator && (
              <>
                <header className="sim-profile-header">
                  <CreatorAvatar
                    creator={selectedCreator}
                    size="profile"
                    story={SPOTLIGHT_HANDLES.includes(selectedCreator.handle)}
                  />
                  <div className="sim-profile-details">
                    <div className="sim-profile-name-row">
                      <h1>{selectedCreator.handle}</h1>
                      {SPOTLIGHT_HANDLES.includes(selectedCreator.handle) && (
                        <span className="sim-spotlight-badge">✦ SPOTLIGHT</span>
                      )}
                    </div>
                    <p className="sim-profile-display-name">{selectedCreator.display_name}</p>
                    <div className="sim-profile-stats">
                      <span><strong>{(selectedCreator.contents || []).length}</strong> posts</span>
                      <span><strong>{formatCount(selectedCreator.follower_count)}</strong> followers</span>
                      <span><strong>{formatCount(selectedCreator.following_count || 0)}</strong> following</span>
                    </div>
                    <p className="sim-profile-bio">{selectedCreator.bio}</p>
                    <span className="sim-niche-pill">{selectedCreator.niche}</span>
                    <button
                      className={`sim-button ${following[selectedCreator.handle] ? 'sim-button--following' : 'sim-button--primary'}`}
                      onClick={() => setFollowing((current) => ({
                        ...current,
                        [selectedCreator.handle]: !current[selectedCreator.handle],
                      }))}
                    >
                      {following[selectedCreator.handle] ? 'Following' : 'Follow'}
                    </button>
                  </div>
                </header>

                <div className="sim-profile-tabs" role="tablist" aria-label="Creator media">
                  <button
                    className={profileTab === 'all' ? 'is-active' : ''}
                    onClick={() => setProfileTab('all')}
                    role="tab"
                    aria-selected={profileTab === 'all'}
                  >
                    <span>▦</span> ALL POSTS
                  </button>
                  <button
                    className={profileTab === 'reels' ? 'is-active' : ''}
                    onClick={() => setProfileTab('reels')}
                    role="tab"
                    aria-selected={profileTab === 'reels'}
                  >
                    <span>▻</span> REELS
                  </button>
                </div>

                {profilePosts.length > 0 ? (
                  <div className="sim-media-grid">
                    {profilePosts.map((content) => (
                      <button
                        className="sim-media-tile"
                        key={content.content_slug}
                        onClick={() => openTheater(content, selectedCreator)}
                        aria-label={`Open ${content.media_type} ${content.content_slug}`}
                      >
                        <img
                          src={resolveMediaUrl(content.thumbnail_path) || undefined}
                          alt={content.caption}
                          loading="lazy"
                        />
                        {content.video_path && (
                          <span className="sim-reel-badge"><span>▶</span> 0:30</span>
                        )}
                        <span className="sim-media-hover">
                          <span>♥ {formatCount(content.likes)}</span>
                          <span>▢ {formatCount(content.comments_count)}</span>
                        </span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="sim-empty-state">
                    <h3>{profileTab === 'reels' ? 'No reels yet' : 'No posts yet'}</h3>
                    <p>This creator has not shared any content in this view.</p>
                  </div>
                )}
              </>
            )}
          </section>
        )}
      </main>

      <Modal open={Boolean(authMode)} onClose={closeAuth} aria-labelledby="sim-auth-title">
        <div className="sim-modal-positioner" tabIndex={-1}>
          <section className="sim-auth-card" role="dialog" aria-modal="true">
            <button className="sim-modal-close" onClick={closeAuth} aria-label="Close login">×</button>
            <span className="sim-eyebrow">{authMode === 'register' ? 'JOIN THE COMMUNITY' : 'DEMO ACCOUNT'}</span>
            <h2 id="sim-auth-title">{authMode === 'register' ? 'Create a demo account' : 'Welcome back'}</h2>
            <p>Use a demo session to follow creators and explore the simulation.</p>
            <form onSubmit={submitAuth} className="sim-auth-form">
              <label htmlFor="sim-auth-username">Username</label>
              <input
                id="sim-auth-username"
                value={authUsername}
                onChange={(event) => setAuthUsername(event.target.value)}
                autoComplete="username"
                required
              />
              {authMode === 'register' && (
                <>
                  <label htmlFor="sim-auth-email">Email (optional)</label>
                  <input
                    id="sim-auth-email"
                    type="email"
                    value={authEmail}
                    onChange={(event) => setAuthEmail(event.target.value)}
                    autoComplete="email"
                  />
                </>
              )}
              <label htmlFor="sim-auth-password">Password</label>
              <input
                id="sim-auth-password"
                type="password"
                value={authPassword}
                onChange={(event) => setAuthPassword(event.target.value)}
                autoComplete={authMode === 'register' ? 'new-password' : 'current-password'}
                required
              />
              {authError && <p className="sim-inline-error" role="alert">{authError}</p>}
              <button className="sim-button sim-button--primary" type="submit" disabled={authBusy}>
                {authBusy ? 'Please wait...' : authMode === 'register' ? 'Register demo user' : 'Log in'}
              </button>
            </form>
            <button
              className="sim-auth-switch"
              onClick={() => { setAuthMode(authMode === 'register' ? 'login' : 'register'); setAuthError(''); }}
            >
              {authMode === 'register' ? 'Already have a demo account? Log in' : 'New here? Register a demo user'}
            </button>
          </section>
        </div>
      </Modal>

      {theaterItem && (
        <Modal open onClose={() => setTheaterItem(null)} aria-label="Post theater">
          <div className="sim-theater-positioner" tabIndex={-1}>
            <section className="sim-theater" role="dialog" aria-modal="true">
              <button className="sim-modal-close sim-theater-close" onClick={() => setTheaterItem(null)} aria-label="Close post">×</button>
              <div className="sim-theater-media">
                {theaterItem.video_path ? (
                  <video
                    src={resolveMediaUrl(theaterItem.video_path)}
                    poster={resolveMediaUrl(theaterItem.thumbnail_path)}
                    controls
                    playsInline
                    preload="metadata"
                    autoPlay
                  />
                ) : (
                  <img
                    src={resolveMediaUrl(theaterItem.thumbnail_path) || undefined}
                    alt={theaterItem.caption || 'Creator post'}
                  />
                )}
              </div>
              <aside className="sim-theater-info">
                <div className="sim-theater-creator">
                  <CreatorAvatar creator={theaterItem.creator || {}} size="small" story />
                  <button onClick={() => { setTheaterItem(null); openCreator(theaterItem.creator?.handle); }}>
                    {theaterItem.creator?.handle || '@creator'}
                  </button>
                </div>
                <p className="sim-theater-caption">{theaterItem.caption}</p>
                <div className="sim-theater-comments">
                  {(theaterItem.comments || []).map((comment, index) => (
                    <p key={comment.id || `${comment.author_handle}-${index}`}>
                      <strong>{comment.author_handle || 'community'}</strong> {comment.text}
                    </p>
                  ))}
                </div>
                <div className="sim-theater-actions">
                  <button
                    className={likedItems[theaterItem.content_slug] ? 'is-liked' : ''}
                    onClick={() => toggleLike(theaterItem)}
                    aria-label="Like post"
                  >
                    {likedItems[theaterItem.content_slug] ? '♥' : '♡'}
                  </button>
                  <strong>{formatCount((Number(theaterItem.likes) || 0) + (likedItems[theaterItem.content_slug] ? 1 : 0))} likes</strong>
                  <span>{theaterItem.comments_count || (theaterItem.comments || []).length} comments</span>
                </div>
              </aside>
            </section>
          </div>
        </Modal>
      )}
    </div>
  );
}

export default App;
