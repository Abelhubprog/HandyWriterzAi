import React from 'react';
import { File, X } from 'lucide-react';

interface FileTileProps {
  fileName: string;
  progress: number;
  onRemove: () => void;
}

export const FileTile: React.FC<FileTileProps> = ({ fileName, progress, onRemove }) => {
  return (
    <div className="relative flex items-center p-2 border rounded-lg bg-slate-700">
      <File className="w-6 h-6 mr-2 text-slate-400" />
      <div className="flex-grow">
        <div className="text-sm font-medium text-slate-200">{fileName}</div>
        <div className="w-full bg-slate-600 rounded-full h-1.5 mt-1">
          <div
            className="bg-blue-500 h-1.5 rounded-full"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
      <button onClick={onRemove} className="ml-2 text-slate-400 hover:text-slate-200">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
