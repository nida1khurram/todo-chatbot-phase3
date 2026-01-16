// frontend/src/components/__tests__/loading-spinner.test.tsx
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '../loading-spinner';

describe('LoadingSpinner', () => {
  test('renders loading spinner', () => {
    render(<LoadingSpinner />);

    const spinner = screen.getByRole('progressbar');
    expect(spinner).toBeInTheDocument();
  });

  test('renders with default size', () => {
    render(<LoadingSpinner />);

    const spinner = screen.getByRole('progressbar');
    expect(spinner).toHaveClass('w-8', 'h-8'); // default md size
  });

  test('renders with small size', () => {
    render(<LoadingSpinner size="sm" />);

    const spinner = screen.getByRole('progressbar');
    expect(spinner).toHaveClass('w-4', 'h-4');
  });

  test('renders with large size', () => {
    render(<LoadingSpinner size="lg" />);

    const spinner = screen.getByRole('progressbar');
    expect(spinner).toHaveClass('w-12', 'h-12');
  });

  test('renders with text when provided', () => {
    render(<LoadingSpinner text="Loading..." />);

    const text = screen.getByText('Loading...');
    expect(text).toBeInTheDocument();
  });

  test('does not render text when not provided', () => {
    render(<LoadingSpinner />);

    const text = screen.queryByText(/loading/i);
    expect(text).not.toBeInTheDocument();
  });

  test('renders with correct border classes', () => {
    render(<LoadingSpinner size="md" />);

    const spinner = screen.getByRole('progressbar');
    expect(spinner).toHaveClass('border-4');
  });
});