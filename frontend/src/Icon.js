import React from 'react';

const iconPaths = {
  home: (
    <>
      <path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />
    </>
  ),
  search: (
    <>
      <circle cx="10.8" cy="10.8" r="6.8" />
      <path d="m16 16 5 5" />
    </>
  ),
  compass: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m15.8 8.2-2.2 5.4-5.4 2.2 2.2-5.4z" />
    </>
  ),
  plus: (
    <>
      <rect x="3.5" y="3.5" width="17" height="17" rx="4" />
      <path d="M12 8v8m-4-4h8" />
    </>
  ),
  instagram: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.8" r=".7" fill="currentColor" stroke="none" />
    </>
  ),
  sparkle: (
    <>
      <path d="M12 2.8 14.2 9l6.3 2.4-6.3 2.2-2.2 6.4-2.3-6.4-6.2-2.2L9.7 9z" />
      <path d="m19 2 .7 2.2L22 5l-2.3.8L19 8l-.8-2.2L16 5l2.2-.8z" />
    </>
  ),
  comment: (
    <>
      <path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H6l-3 2v-5.2A7.5 7.5 0 1 1 20 11.5Z" />
      <path d="M8 11.5h8m-8 3h5" />
    </>
  ),
  more: (
    <>
      <circle cx="5" cy="12" r="1" fill="currentColor" />
      <circle cx="12" cy="12" r="1" fill="currentColor" />
      <circle cx="19" cy="12" r="1" fill="currentColor" />
    </>
  ),
  close: (
    <>
      <path d="m6 6 12 12M18 6 6 18" />
    </>
  ),
  camera: (
    <>
      <path d="M4 7h3l1.5-2h7L17 7h3v12H4z" />
      <circle cx="12" cy="13" r="3.5" />
      <path d="M17.5 10h.01" />
    </>
  ),
  refresh: (
    <>
      <path d="M20 7v5h-5M4 17v-5h5" />
      <path d="M5.7 9A7 7 0 0 1 18 6l2 2m-16 8 2 2a7 7 0 0 0 12.3-3" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M2.8 20a6.2 6.2 0 0 1 12.4 0M16 5a3.5 3.5 0 0 1 0 6.8m1.8 2a5.5 5.5 0 0 1 3.4 5.1" />
    </>
  ),
};

function Icon({ name }) {
  return (
    <svg
      className="ui-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {iconPaths[name] || iconPaths.sparkle}
    </svg>
  );
}

export default Icon;
