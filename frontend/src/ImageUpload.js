import React, { useEffect, useRef, useState } from 'react';
import './ImageUpload.css';
import Icon from './Icon';
import { apiUrl } from './api';

function ImageUpload({ authToken, authTokenType, userId, username, onPostCreated }) {
  const [caption, setCaption] = useState('');
  const [title, setTitle] = useState('');
  const [image, setImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState('');

  useEffect(() => {
    if (!image) {
      setPreviewUrl('');
      return undefined;
    }

    const objectUrl = URL.createObjectURL(image);
    setPreviewUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [image]);

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!image || isUploading) {
      return;
    }

    setIsUploading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('img', image);
      const uploadResponse = await fetch(apiUrl('post/image'), {
        method: 'POST',
        headers: new Headers({ Authorization: `${authTokenType} ${authToken}` }),
        body: formData,
      });
      const uploadData = await uploadResponse.json();
      if (!uploadResponse.ok) {
        throw new Error(uploadData.detail || `Image upload failed (${uploadResponse.status}).`);
      }

      const postResponse = await fetch(apiUrl('post/create'), {
        method: 'POST',
        headers: new Headers({
          Authorization: `${authTokenType} ${authToken}`,
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
          post_title: title.trim() || 'A moment shared',
          image_url: uploadData.url,
          image_url_type: 'relative',
          caption: caption.trim(),
          user_id: Number(userId),
        }),
      });
      const postData = await postResponse.json();
      if (!postResponse.ok) {
        throw new Error(postData.detail || `Could not create post (${postResponse.status}).`);
      }

      onPostCreated({
        ...postData,
        user_id: Number(userId),
        user: postData.user || { username },
        comments: postData.comments || [],
      });
      setCaption('');
      setTitle('');
      setImage(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <section className="composer-card" aria-label="Create a post">
      <div className="composer-heading">
        <div>
          <span className="eyebrow">MAKE SOMETHING MEMORABLE</span>
          <h2>Share a moment</h2>
        </div>
        <span className="composer-heading-icon"><Icon name="plus" /></span>
      </div>

      <form className="composer-form" onSubmit={handleUpload}>
        <div className={`image-picker${previewUrl ? ' image-picker--preview' : ''}`}>
          {previewUrl ? (
            <img src={previewUrl} alt="Preview of the selected upload" />
          ) : (
            <div className="image-picker-prompt">
              <span className="image-picker-icon"><Icon name="camera" /></span>
              <strong>Choose a photo</strong>
              <span>JPG, PNG or GIF</span>
            </div>
          )}
          <input
            ref={fileInputRef}
            id="fileInput"
            className="visually-hidden"
            type="file"
            accept="image/*"
            onChange={(event) => setImage(event.target.files?.[0] || null)}
            aria-label="Choose an image"
          />
          <button
            className="image-picker-button"
            type="button"
            onClick={() => fileInputRef.current?.click()}
          >
            {previewUrl ? 'Change photo' : 'Choose photo'}
          </button>
        </div>

        <div className="composer-fields">
          <label htmlFor="post-title">A title for this moment</label>
          <input
            id="post-title"
            type="text"
            placeholder="A moment shared"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            maxLength={256}
          />
          <label htmlFor="post-caption">Add a caption</label>
          <textarea
            id="post-caption"
            placeholder="What made this moment special?"
            value={caption}
            onChange={(event) => setCaption(event.target.value)}
            maxLength={512}
            rows={3}
          />
          {error && <p className="composer-error" role="alert">{error}</p>}
          <button className="primary-button composer-submit" type="submit" disabled={!image || isUploading}>
            {isUploading ? 'Sharing your moment…' : 'Share post'}
          </button>
        </div>
      </form>
    </section>
  );
}

export default ImageUpload;
