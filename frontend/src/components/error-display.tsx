// frontend/src/components/error-display.tsx
interface ErrorDisplayProps {
  error: string | null;
  onClose?: () => void;
}

export const ErrorDisplay = ({ error, onClose }: ErrorDisplayProps) => {
  if (!error) return null;

  return (
    <div className="rounded-md bg-red-50 p-4 mb-4">
      <div className="flex items-start">
        <div className="flex-shrink-0 pt-0.5">
          <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1 min-w-0">
          <h3 className="text-sm font-medium text-red-800 break-words">{error}</h3>
        </div>
        {onClose && (
          <div className="ml-4 flex-shrink-0">
            <button
              type="button"
              className="inline-flex rounded-md bg-red-50 p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2"
              onClick={onClose}
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};