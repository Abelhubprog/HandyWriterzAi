"use client";

import * as React from "react";
import Textarea from "react-textarea-autosize";
import { Button } from "@/components/ui/button";
import { ContextUploadMenu } from "./ContextUploadMenu";
import { CostMeter } from "./CostMeter";

export function PromptEditor({
  onSubmit,
  isLoading,
}: {
  onSubmit: (value: string) => Promise<void>;
  isLoading: boolean;
}) {
  const [value, setValue] = React.useState("");
  const inputRef = React.useRef<HTMLTextAreaElement>(null);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim()) {
        onSubmit(value);
        setValue("");
      }
    }
  };

  return (
    <div className="relative flex max-h-[50vh] w-full grow flex-col overflow-hidden bg-background px-8 sm:rounded-md sm:border sm:px-12">
      <Textarea
        ref={inputRef}
        tabIndex={0}
        onKeyDown={onKeyDown}
        rows={1}
        value={value}
        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setValue(e.target.value)}
        placeholder="Send a message."
        spellCheck={false}
        className="w-full resize-none bg-transparent focus-within:outline-none sm:text-sm"
      />
      <div className="absolute right-4 top-2/4 -translate-y-2/4">
        <div className="flex items-center space-x-2">
          <CostMeter prompt={value} />
          <ContextUploadMenu />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !value.trim()}
            onClick={() => onSubmit(value)}
          >
            <span>Send</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
