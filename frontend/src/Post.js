import React, { useState } from 'react';
import './Post.css';
import { resolveMediaUrl } from './api';

function Avatar({ creator = {} }) {
  const safeCreator = creator && typeof creator === 'object' ? creator : {};
  const name = [safeCreator.display_name, safeCreator.handle]
    .find((value) => typeof value === 'string' && value.trim()) || 'Creator';
  return (
    <span className="post-avatar">
      {safeCreator.avatar_url
        ? <img src={resolveMediaUrl(safeCreator.avatar_url)} alt="" />
        : name.trim().slice(0, 1).toUpperCase()}
    </span>
  );
}

function formatDate(value) {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(date);
}

function Post({
  post,
  onCreatorClick = () => {},
  onOpenTheater = () => {},
  animationIndex = 0,
}) {
  const [liked, setLiked] = useState(false);
  const safePost = post && typeof post === 'object' ? post : {};
  const creator = safePost.creator && typeof safePost.creator === 'object' && !Array.isArray(safePost.creator)
    ? safePost.creator
    : {};
  const handle = typeof creator.handle === 'string' && creator.handle ? creator.handle : '@creator';
  const niche = typeof creator.niche === 'string' && creator.niche ? creator.niche : 'Creator';
  const thumbUrl = resolveMediaUrl(safePost.thumbnail_path);
  const mediaUrl = resolveMediaUrl(safePost.video_path);
  const comments = Array.isArray(safePost.comments)
    ? safePost.comments.filter((comment) => comment && typeof comment === 'object')
    : [];

  return (
    <article
      className="post-card"
      style={{ '--post-delay': `${Math.min(animationIndex, 5) * 55}ms` }}
    >
      <header className="post-header">
        <div className="post-identity">
          <button
            className="post-avatar-button"
            onClick={() => onCreatorClick(handle)}
            aria-label={`Open ${handle}'s profile`}
          >
            <Avatar creator={creator} />
          </button>
          <div className="post-identity-copy">
            <button className="post-handle-button" onClick={() => onCreatorClick(handle)}>
              {handle}
              {creator.is_demo_creator && <span className="post-verified" aria-label="Spotlight creator">✓</span>}
            </button>
            <span>{niche}{formatDate(safePost.posted_at) ? ` · ${formatDate(safePost.posted_at)}` : ''}</span>
          </div>
        </div>
        <span className="post-media-label">{safePost.media_type === 'post' ? 'PHOTO' : 'REEL'}</span>
      </header>

      <div className="post-image-frame">
        {safePost.video_path ? (
          <video
            className="post-video"
            src={mediaUrl}
            poster={thumbUrl}
            controls
            playsInline
            preload="metadata"
          />
        ) : (
          <button
            className="post-photo-button"
            onClick={() => onOpenTheater(safePost)}
            aria-label={`Open photo by ${handle}`}
          >
            <img
              className="post-image"
              src={thumbUrl || undefined}
              alt={safePost.caption || 'Creator post'}
              loading="lazy"
            />
          </button>
        )}
      </div>

      <div className="post-content">
        <div className="post-reaction-row">
          <button
            className={`post-like-button${liked ? ' post-like-button--liked' : ''}`}
            onClick={() => setLiked((current) => !current)}
            aria-label={liked ? 'Unlike post' : 'Like post'}
            aria-pressed={liked}
          >
            {liked ? '♥' : '♡'}
          </button>
          <span className="post-like-count">{(Number(safePost.likes) || 0) + (liked ? 1 : 0)} likes</span>
          <button className="post-comment-link" onClick={() => onOpenTheater(safePost)}>
            {comments.length} {comments.length === 1 ? 'comment' : 'comments'}
          </button>
        </div>

        {safePost.caption && (
          <p className="post-caption">
            <button className="post-caption-handle" onClick={() => onCreatorClick(handle)}>{handle}</button>
            <span>{safePost.caption}</span>
          </p>
        )}

        {comments.slice(0, 2).map((comment, index) => (
          <p className="post-comment" key={comment.id || `${comment.author_handle}-${index}`}>
            <strong>{comment.author_handle || 'community'} </strong>
            <span>{comment.text}</span>
          </p>
        ))}
        {comments.length > 2 && (
          <button className="post-view-comments" onClick={() => onOpenTheater(safePost)}>
            View all {comments.length} comments
          </button>
        )}
      </div>
    </article>
  );
}

export default Post;
