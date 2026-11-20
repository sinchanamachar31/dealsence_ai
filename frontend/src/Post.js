import React, { useRef, useState } from 'react';
import './Post.css';
import Icon from './Icon';
import { apiUrl } from './api';

function Avatar({ name }) {
  return <span className="post-avatar" aria-hidden="true">{(name || '?').trim().slice(0, 1).toUpperCase()}</span>;
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

function Post({ post, authToken, authTokenType, username, canDelete, onDelete, onLogin, animationIndex = 0 }) {
  const [comments, setComments] = useState(post.comments || []);
  const [newComment, setNewComment] = useState('');
  const [isPostingComment, setIsPostingComment] = useState(false);
  const commentInputRef = useRef(null);
  const imageUrl = post.image_url_type === 'absolute' ? post.image_url : apiUrl(post.image_url);

  const handleDelete = async () => {
    if (!window.confirm('Delete this post? This cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(apiUrl(`post/delete/${post.id}`), {
        method: 'DELETE',
        headers: new Headers({ Authorization: `${authTokenType} ${authToken}` }),
      });
      if (!response.ok) {
        throw new Error(`Could not delete post (${response.status}).`);
      }
      onDelete(post.id);
    } catch (error) {
      window.alert(error.message);
    }
  };

  const postComment = async (event) => {
    event.preventDefault();
    const text = newComment.trim();
    if (!text || isPostingComment) {
      return;
    }

    setIsPostingComment(true);
    try {
      const response = await fetch(apiUrl('post/new-comment'), {
        method: 'POST',
        headers: new Headers({
          Authorization: `${authTokenType} ${authToken}`,
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
          username,
          text,
          likes: 0,
          post_id: post.id,
        }),
      });
      if (!response.ok) {
        throw new Error(`Could not post comment (${response.status}).`);
      }

      const commentsResponse = await fetch(apiUrl(`post/all-comment/${post.id}`));
      if (!commentsResponse.ok) {
        throw new Error(`Could not refresh comments (${commentsResponse.status}).`);
      }
      setComments(await commentsResponse.json());
      setNewComment('');
    } catch (error) {
      window.alert(error.message);
    } finally {
      setIsPostingComment(false);
    }
  };

  const creatorName = post.user?.username || 'Someone';

  return (
    <article
      className="post-card"
      style={{ '--post-delay': `${Math.min(animationIndex, 5) * 70}ms` }}
    >
      <header className="post-header">
        <div className="post-identity">
          <Avatar name={creatorName} />
          <div className="post-identity-copy">
            <strong>{creatorName}</strong>
            <span>{post.post_title || 'A moment shared'}{formatDate(post.created_at) ? ` · ${formatDate(post.created_at)}` : ''}</span>
          </div>
        </div>
        {canDelete && (
          <button className="post-menu-button" onClick={handleDelete} aria-label="Delete your post" title="Delete post">
            <Icon name="more" />
          </button>
        )}
      </header>

      <div className="post-image-frame">
        <img className="post-image" src={imageUrl} alt={post.caption || post.post_title || 'Shared moment'} loading="lazy" />
      </div>

      <div className="post-content">
        <div className="post-reaction-row">
          <button
            className="post-reaction-button"
            onClick={() => commentInputRef.current?.focus()}
            aria-label="Write a comment"
            title="Write a comment"
          >
            <Icon name="comment" />
          </button>
          <span className="comment-count">{comments.length > 0 ? `${comments.length} ${comments.length === 1 ? 'comment' : 'comments'}` : 'Start the conversation'}</span>
          <span className="post-content-sparkle" aria-hidden="true"><Icon name="sparkle" /></span>
        </div>

        {post.caption && (
          <p className="post-caption">
            <strong>{creatorName}</strong>
            <span>{post.caption}</span>
          </p>
        )}

        {comments.length > 0 && (
          <div className="post-comments" aria-label="Comments">
            {comments.map((comment) => (
              <p className="post-comment" key={comment.id || `${comment.username}-${comment.text}-${comment.timestamp}`}>
                <strong>{comment.username} </strong>
                <span>{comment.text}</span>
              </p>
            ))}
          </div>
        )}

        {authToken ? (
          <form className="post-comment-form" onSubmit={postComment}>
            <input
              ref={commentInputRef}
              type="text"
              placeholder="Add a thoughtful comment…"
              value={newComment}
              onChange={(event) => setNewComment(event.target.value)}
              aria-label="Write a comment"
            />
            <button type="submit" disabled={!newComment.trim() || isPostingComment}>
              {isPostingComment ? 'Sending…' : 'Post'}
            </button>
          </form>
        ) : (
          <button className="post-login-prompt"           onClick={onLogin}>
            Log in to join the conversation
          </button>
        )}
      </div>
    </article>
  );
}

export default Post;
