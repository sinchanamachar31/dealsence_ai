import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  window.localStorage.clear();
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
  });
});

afterEach(() => {
  jest.restoreAllMocks();
});

test('shows the feed empty state after loading posts', async () => {
  render(<App />);

  expect(await screen.findByRole('heading', { name: 'Your feed' })).toBeInTheDocument();
  expect(await screen.findByRole('heading', { name: 'Your feed is ready for its first moment.' })).toBeInTheDocument();
});

test('opens the login dialog from the navigation', async () => {
  render(<App />);

  fireEvent.click(screen.getAllByRole('button', { name: 'Log in' })[0]);

  expect(await screen.findByRole('dialog', { name: 'Welcome back' })).toBeInTheDocument();
  expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/post/all'));
});
