import { QUICK_PROMPTS } from '../constants';

interface QuickPromptRowProps {
  isLoading: boolean;
  onPromptClick: (message: string) => void;
}

export function QuickPromptRow({ isLoading, onPromptClick }: QuickPromptRowProps) {
  return (
    <div className="mb-3 flex flex-wrap gap-2">
      {QUICK_PROMPTS.map((prompt) => (
        <button
          key={prompt.message}
          type="button"
          onClick={() => onPromptClick(prompt.message)}
          disabled={isLoading}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-left text-sm text-gray-700 transition hover:border-blue-400 hover:bg-blue-50 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-400"
        >
          {prompt.label}
        </button>
      ))}
    </div>
  );
}