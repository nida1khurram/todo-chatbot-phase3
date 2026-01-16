// frontend/src/components/__tests__/error-display.test.tsx
import { render, screen } from '@testing-library/react';
import { ErrorDisplay } from '../error-display';

describe('ErrorDisplay', () => {
  test('renders error message when error is provided', () => {
    render(<ErrorDisplay error="This is an error message" />);

    const errorMessage = screen.getByText('This is an error message');
    expect(errorMessage).toBeInTheDocument();
  });

  test('does not render when no error is provided', () => {
    render(<ErrorDisplay error={null} />);

    const errorMessage = screen.queryByText(/error/i);
    expect(errorMessage).not.toBeInTheDocument();
  });

  test('renders error message when error is empty string', () => {
    render(<ErrorDisplay error="" />);

    // An empty string should be treated as falsy, so no error should be shown
    const errorMessage = screen.queryByText(/error/i);
    expect(errorMessage).not.toBeInTheDocument();
  });

  test('renders error message when error is a valid string', () => {
    const errorMessage = "Something went wrong";
    render(<ErrorDisplay error={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });
});