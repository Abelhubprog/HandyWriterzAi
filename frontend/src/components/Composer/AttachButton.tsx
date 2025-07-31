'use client';

import React, { useRef } from 'react';
import { Plus, Camera, Image, FileText } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AttachButtonProps {
  onFiles: (files: FileList) => void;
  disabled?: boolean;
}

export function AttachButton({ onFiles, disabled }: AttachButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleScreenshot = async () => {
    try {
      // Check if the Screen Capture API is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        throw new Error('Screen capture not supported');
      }

      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { mediaSource: 'screen' } as any,
      });

      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      video.onloadedmetadata = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');

        if (ctx) {
          ctx.drawImage(video, 0, 0);

          canvas.toBlob((blob) => {
            if (blob) {
              const file = new File([blob], `screenshot-${Date.now()}.png`, { type: 'image/png' });
              const dt = new DataTransfer();
              dt.items.add(file);
              onFiles(dt.files);
            }

            // Stop the stream
            stream.getTracks().forEach(track => track.stop());
          }, 'image/png');
        }
      };
    } catch (error) {
      console.error('Screenshot failed:', error);
    }
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleCameraSelect = () => {
    cameraInputRef.current?.click();
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-10 w-10 rounded-lg",
              "hover:bg-accent hover:text-accent-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            )}
            disabled={disabled}
          >
            <Plus className="h-5 w-5" />
            <span className="sr-only">Attach files</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48">
          <DropdownMenuItem onClick={handleScreenshot}>
            <Camera className="mr-2 h-4 w-4" />
            Take screenshot
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleCameraSelect}>
            <Image className="mr-2 h-4 w-4" />
            Take photo
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleFileSelect}>
            <FileText className="mr-2 h-4 w-4" />
            Add photos & files
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={(e) => e.target.files && onFiles(e.target.files)}
        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.xls"
      />
      <input
        ref={cameraInputRef}
        type="file"
        capture="environment"
        accept="image/*"
        className="hidden"
        onChange={(e) => e.target.files && onFiles(e.target.files)}
      />
    </>
  );
}
