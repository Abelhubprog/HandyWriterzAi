'use client'

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Brain, Copy, ThumbsUp, ThumbsDown, Check, Pencil, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DownloadMenu } from '@/components/DownloadMenu';
import { ResponseActions } from '@/components/ResponseActions';
import type { Message } from '@/types';

interface MessageBubbleProps {
  message: Message;
  isLast: boolean;
  reasoning?: string;
  traceId?: string | null;
  totalCost?: number;
  plagiarismScore?: number;
  qualityScore?: number;
  derivatives?: { kind: string; url: string }[];
}

export function MessageBubble({
  message,
  isLast,
  reasoning,
  traceId,
  totalCost,
  plagiarismScore,
  qualityScore,
  derivatives = []
}: MessageBubbleProps) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState<string>(
    typeof message.content === 'string' ? message.content : JSON.stringify(message.content)
  );

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleFeedback = (type: 'positive' | 'negative') => {
    // TODO: Implement feedback API call
    console.log(`Feedback: ${type} for message ${message.id}`);
  };

  if (message.type === 'human') {
    const text = typeof message.content === 'string' ? message.content : JSON.stringify(message.content);
    return (
      <div className="mb-6 w-full">
        <div className="flex justify-end">
          {/* Relative wrapper to anchor the external bottom-right action bar */}
          <div className="max-w-[70%] min-w-0 relative group">
            {/* Actions: Copy + Edit - bottom-right, outside bubble, inline glyphs, hover/focus fade-in */}
            <div className="pointer-events-none absolute bottom-[-6px] right-[-6px] opacity-0 transition-opacity duration-150 ease-out group-hover:opacity-100 group-focus-within:opacity-100 z-10">
              <div className="pointer-events-auto flex items-center gap-2 bg-transparent">
                <button
                  aria-label="Copy message"
                  onClick={() => handleCopy(isEditing ? draft : text)}
                  className="h-5 w-5 text-white/90 hover:text-white transition-colors"
                  title={copied ? 'Copied!' : 'Copy'}
                >
                  {copied ? <Check className="h-5 w-5" /> : <Copy className="h-5 w-5" />}
                </button>

                {!isEditing ? (
                  <button
                    aria-label="Edit message"
                    onClick={() => { setIsEditing(true); setDraft(text); }}
                    className="h-5 w-5 text-white/90 hover:text-white transition-colors"
                    title="Edit"
                  >
                    <Pencil className="h-5 w-5" />
                  </button>
                ) : (
                  <button
                    aria-label="Cancel edit"
                    onClick={() => { setIsEditing(false); setDraft(text); }}
                    className="h-5 w-5 text-white/90 hover:text-white transition-colors"
                    title="Cancel"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>

            <div className="bg-primary text-primary-foreground px-4 py-3 rounded-2xl rounded-br-md">
              {isEditing ? (
                <div className="space-y-2">
                  <textarea
                    className="w-full bg-white/10 text-primary-foreground text-sm rounded-md p-2 outline-none resize-y"
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    rows={Math.min(12, Math.max(3, Math.ceil((draft || '').length / 80)))}
                  />
                  <div className="flex gap-2 justify-end">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => { setIsEditing(false); setDraft(text); }}
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => {
                        // Local-only edit: update current render without persisting to store
                        (message as any).content = draft;
                        setIsEditing(false);
                      }}
                    >
                      Save
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-sm whitespace-pre-wrap break-words overflow-wrap-anywhere">
                  {text}
                </div>
              )}
            </div>

            <div className="text-xs text-muted-foreground mt-1 text-right">
              You • {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'now'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6 w-full">
      <div className="flex justify-start">
        {/* Relative wrapper to anchor the external bottom-right action bar */}
        <div className="max-w-[85%] min-w-0 relative group">
          {/* Actions: Copy + Edit - bottom-right, outside bubble, inline glyphs, hover/focus fade-in */}
          <div className="pointer-events-none absolute bottom-[-6px] right-[-6px] opacity-0 transition-opacity duration-150 ease-out group-hover:opacity-100 group-focus-within:opacity-100 z-10">
            <div className="pointer-events-auto flex items-center gap-2 bg-transparent">
              <button
                aria-label="Copy message"
                onClick={() =>
                  handleCopy(typeof message.content === 'string' ? message.content : JSON.stringify(message.content))
                }
                className="h-5 w-5 text-foreground/70 hover:text-foreground transition-colors"
                title={copied ? 'Copied!' : 'Copy'}
              >
                {copied ? <Check className="h-5 w-5" /> : <Copy className="h-5 w-5" />}
              </button>

              {/* Enable inline edit for assistant messages too */}
              {!isEditing ? (
                <button
                  aria-label="Edit message"
                  onClick={() => {
                    setIsEditing(true);
                    setDraft(typeof message.content === 'string' ? message.content : JSON.stringify(message.content));
                  }}
                  className="h-5 w-5 text-foreground/70 hover:text-foreground transition-colors"
                  title="Edit"
                >
                  <Pencil className="h-5 w-5" />
                </button>
              ) : (
                <button
                  aria-label="Cancel edit"
                  onClick={() => {
                    setIsEditing(false);
                    setDraft(typeof message.content === 'string' ? message.content : JSON.stringify(message.content));
                  }}
                  className="h-5 w-5 text-foreground/70 hover:text-foreground transition-colors"
                  title="Cancel"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
          <div className="bg-secondary text-foreground px-4 py-3 rounded-2xl rounded-bl-md">
            {isEditing ? (
              <div className="space-y-2">
                <textarea
                  className="w-full bg-background/60 text-foreground text-sm rounded-md p-2 outline-none resize-y"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  rows={Math.min(12, Math.max(3, Math.ceil((draft || '').length / 80)))}
                />
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setIsEditing(false);
                      setDraft(typeof message.content === 'string' ? message.content : JSON.stringify(message.content));
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => {
                      // Local-only edit for assistant too
                      (message as any).content = draft;
                      setIsEditing(false);
                    }}
                  >
                    Save
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-sm whitespace-pre-wrap break-words overflow-wrap-anywhere leading-relaxed">
                {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
              </div>
            )}

            {/* Reasoning Toggle */}
            {reasoning && (
              <div className="mt-4 border-t border-border pt-3">
                <button
                  onClick={() => setShowReasoning(!showReasoning)}
                  className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showReasoning ? (
                    <ChevronDown className="h-3 w-3" />
                  ) : (
                    <ChevronRight className="h-3 w-3" />
                  )}
                  <Brain className="h-3 w-3" />
                  Show reasoning
                </button>

                {showReasoning && (
                  <div className="mt-2 p-3 bg-muted/50 rounded-lg border border-border">
                    <div className="text-xs text-muted-foreground font-mono whitespace-pre-wrap break-words">
                      {reasoning}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Download Menu for completed responses */}
            {isLast && traceId && derivatives.length > 0 && (
              <div className="mt-4 border-t border-border pt-3">
                <DownloadMenu
                  traceId={traceId}
                  derivatives={derivatives}
                  plagiarismScore={plagiarismScore}
                  qualityScore={qualityScore}
                  onOriginalityCheck={() => {
                    window.open(`/originality/${traceId}`, '_blank');
                  }}
                />
              </div>
            )}
          </div>

          {/* Message Actions - ChatGPT Style */}
          <div className="flex items-center justify-between mt-2">
            <div className="text-xs text-muted-foreground">
              HandyWriterz • {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'now'}
            </div>

            <ResponseActions
              messageId={message.id || 'unknown'}
              messageContent={typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
              conversationId={traceId}
            />
          </div>

          {/* Metrics for completed responses */}
          {isLast && (totalCost > 0 || plagiarismScore > 0 || qualityScore > 0) && (
            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
              {totalCost > 0 && <span>Cost: ${totalCost.toFixed(4)}</span>}
              {plagiarismScore > 0 && <span>Originality: {(100 - plagiarismScore).toFixed(1)}%</span>}
              {qualityScore > 0 && <span>Quality: {qualityScore.toFixed(1)}%</span>}
            </div>
          )}

          {copied && (
            <div className="text-xs text-green-400 mt-1">
              Copied to clipboard!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
