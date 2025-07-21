import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { usePrefsStore } from '@/store/usePrefs';

export const ModelPreference: React.FC = () => {
  const { model, setModel } = usePrefsStore();

  return (
    <div className="p-4">
      <h3 className="text-lg font-medium">Default Model</h3>
      <p className="text-sm text-muted-foreground mb-4">
        Choose the default model for the chat composer.
      </p>
      <Select value={model} onValueChange={setModel}>
        <SelectTrigger className="w-[280px]">
          <SelectValue placeholder="Select a model" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="gemini-1.5-flash-preview-04-17">Gemini 1.5 Flash</SelectItem>
          <SelectItem value="gemini-1.5-pro-preview-05-06">Gemini 1.5 Pro</SelectItem>
          <SelectItem value="claude-3-opus-20240229">Claude 3 Opus</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
};