'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface MicButtonProps {
  onTranscript: (transcript: string) => void;
  disabled?: boolean;
}

export function MicButton({ onTranscript, disabled }: MicButtonProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isSupported, setIsSupported] = useState(true);

  const recognitionRef = useRef<any>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    // Check if Web Speech API is supported
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (!SpeechRecognition) {
        setIsSupported(false);
        return;
      }

      // Initialize speech recognition
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        if (finalTranscript) {
          onTranscript(finalTranscript.trim());
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        stopRecording();
      };

      recognition.onend = () => {
        if (isRecording) {
          // Restart if still recording (happens on silence)
          try {
            recognition.start();
          } catch (e) {
            stopRecording();
          }
        }
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording, onTranscript]);

  const startRecording = useCallback(() => {
    if (!recognitionRef.current || disabled) return;

    try {
      recognitionRef.current.start();
      setIsRecording(true);
      startTimeRef.current = Date.now();

      // Update timer every 100ms
      timerRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setRecordingTime(elapsed);
      }, 100);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  }, [disabled]);

  const stopRecording = useCallback(() => {
    if (!recognitionRef.current) return;

    try {
      recognitionRef.current.stop();
      setIsRecording(false);
      setRecordingTime(0);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
    }
  }, []);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isSupported) {
    return null;
  }

  return (
    <div className="relative flex items-center">
      {isRecording && (
        <span className="absolute -left-12 text-xs text-muted-foreground font-mono">
          {formatTime(recordingTime)}
        </span>
      )}
      <Button
        variant="ghost"
        size="icon"
        onClick={toggleRecording}
        disabled={disabled}
        className={cn(
          "h-10 w-10 rounded-lg transition-all",
          "hover:bg-accent hover:text-accent-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          isRecording && "text-destructive animate-pulse"
        )}
      >
        {isRecording ? (
          <MicOff className="h-5 w-5" />
        ) : (
          <Mic className="h-5 w-5" />
        )}
        <span className="sr-only">
          {isRecording ? 'Stop recording' : 'Start recording'}
        </span>
      </Button>
    </div>
  );
}
