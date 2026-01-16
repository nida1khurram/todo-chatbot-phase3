// frontend/src/components/loading-spinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const LoadingSpinner = ({ size = 'md', text }: LoadingSpinnerProps) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const borderSize = {
    sm: 'border-2',
    md: 'border-4',
    lg: 'border-4'
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`${sizeClasses[size]} ${borderSize[size]} border-gray-200 border-t-indigo-600 rounded-full animate-spin flex-shrink-0`}></div>
      {text && <p className="mt-2 text-sm text-gray-600 text-center">{text}</p>}
    </div>
  );
};