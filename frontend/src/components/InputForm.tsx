import React, { useState, useRef, useEffect, useCallback } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { Button } from "@/components/ui/button";
import { SquarePen, Brain, Send, StopCircle, Zap, Cpu, Paperclip, X, Plus, ArrowUp, Camera, FolderOpen, Settings, Mic, ScreenShare } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { usePrefsStore } from "@/store/usePrefs";
import { ContextUploader } from "./ui/ContextUploader";
import { MicButton } from "./chat/MicButton";

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, writeupType: string, model: string, fileIds: string[]) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

const InputFormComponent: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");
  const [writeupType, setWriteupType] = useState("general");
  const { model } = usePrefsStore();
  const [fileIds, setFileIds] = useState<string[]>([]);
  const [showUploader, setShowUploader] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Memoize callbacks to prevent unnecessary re-renders
  const handleWriteupTypeChange = useCallback((value: string) => {
    setWriteupType(value);
  }, []);

  const autoResize = useCallback((el: HTMLTextAreaElement) => {
    el.style.height = "auto";
    const maxHeight = 300; // Maximum height in pixels
    const newHeight = Math.min(el.scrollHeight, maxHeight);
    el.style.height = `${newHeight}px`;
    el.style.overflowY = newHeight >= maxHeight ? "auto" : "hidden";
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      autoResize(textareaRef.current);
    }
  }, [internalInputValue, autoResize]);

  const handleInternalSubmit = useCallback((e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim() && fileIds.length === 0) return;
    onSubmit(internalInputValue, writeupType, model, fileIds);
    setInternalInputValue("");
    setFileIds([]);
    setShowUploader(false);
  }, [internalInputValue, writeupType, model, fileIds, onSubmit]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleInternalSubmit();
    }
  }, [handleInternalSubmit]);

  const isSubmitDisabled = (!internalInputValue.trim() && fileIds.length === 0) || isLoading;

  const handleTakeScreenshot = async () => {
    try {
      // Request screen sharing permission for screenshot capture
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false
      });
      
      // Create a video element to capture the screenshot
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();
      
      video.onloadedmetadata = () => {
        // Create canvas to capture the frame
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(video, 0, 0);
        
        // Convert to blob and add to files
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], `screenshot-${Date.now()}.png`, { type: 'image/png' });
            // This would need integration with file upload system
            console.log('Screenshot captured:', file);
          }
        }, 'image/png');
        
        // Stop the stream
        stream.getTracks().forEach(track => track.stop());
      };
    } catch (error) {
      console.error('Error taking screenshot:', error);
    }
  };

  const handleTakePhoto = async () => {
    try {
      // Request camera permission
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      
      // Create a video element to show camera feed
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();
      
      // Create a modal or inline camera interface
      // For now, we'll auto-capture after a short delay
      setTimeout(() => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(video, 0, 0);
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], `photo-${Date.now()}.jpg`, { type: 'image/jpeg' });
            // This would need integration with file upload system
            console.log('Photo captured:', file);
          }
        }, 'image/jpeg');
        
        // Stop the stream
        stream.getTracks().forEach(track => track.stop());
      }, 3000); // 3 second delay for user to position camera
      
    } catch (error) {
      console.error('Error taking photo:', error);
    }
  };

  const handleAddFiles = () => {
    setShowUploader(!showUploader);
  };

  const handleTools = () => {
    // Implementation for tools - could open a tools sidebar or modal
    console.log("Tools clicked");
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="flex flex-col gap-4 p-6">
        {showUploader && <ContextUploader onFileIdsChange={setFileIds} />}
        
        {/* Main input container */}
        <div className="relative">
          <div className="relative bg-gray-800 rounded-2xl border border-gray-700 p-1">
            <div className="flex items-start gap-2">
              {/* Plus button dropdown */}
              <div className="flex-shrink-0 mt-3 ml-3">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      type="button"
                      size="icon"
                      className="bg-transparent hover:bg-gray-700 h-8 w-8 text-gray-400 hover:text-white"
                    >
                      <Plus className="h-5 w-5" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="w-56 bg-gray-800 text-white border-gray-700">
                    <DropdownMenuItem onClick={handleTakeScreenshot} className="flex items-center gap-2 hover:bg-gray-700 cursor-pointer">
                      <ScreenShare className="h-4 w-4" />
                      Take screenshot
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleTakePhoto} className="flex items-center gap-2 hover:bg-gray-700 cursor-pointer">
                      <Camera className="h-4 w-4" />
                      Take photo
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleAddFiles} className="flex items-center gap-2 hover:bg-gray-700 cursor-pointer">
                      <FolderOpen className="h-4 w-4" />
                      Add photos & files
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleTools} className="flex items-center gap-2 hover:bg-gray-700 cursor-pointer">
                      <Settings className="h-4 w-4" />
                      Tools
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* Input field */}
              <div className="flex-grow">
                <Textarea
                  ref={textareaRef}
                  value={internalInputValue}
                  onChange={(e) => {
                    if (e.target.value.length > 15000) {
                      return;
                    }
                    setInternalInputValue(e.target.value)
                  }}
                  onInput={(e) => autoResize(e.currentTarget)}
                  onKeyDown={handleKeyDown}
                  placeholder="How can I help you today?"
                  className="w-full bg-transparent border-none px-2 py-3 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-0 min-h-[56px] overflow-y-auto"
                  rows={1}
                  aria-label="Prompt"
                  style={{ 
                    maxHeight: '300px',
                    wordWrap: 'break-word',
                    whiteSpace: 'pre-wrap'
                  }}
                />
              </div>

              {/* Right side buttons */}
              <div className="flex items-center gap-2 mt-3 mr-3">
                <MicButton onTranscript={setInternalInputValue} />
                <Button
                  type="submit"
                  size="icon"
                  className="rounded-full bg-white text-black p-2 h-10 w-10 hover:bg-gray-200 active:scale-95 transition disabled:opacity-50"
                  disabled={isSubmitDisabled}
                  onClick={handleInternalSubmit}
                >
                  {isLoading ? (
                    <StopCircle className="h-6 w-6 text-red-500" onClick={onCancel} />
                  ) : (
                    <ArrowUp className="h-6 w-6" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Mode selector */}
        <div className="flex items-center justify-center">
          <Select value={writeupType} onValueChange={handleWriteupTypeChange}>
            <SelectTrigger className="w-[200px] bg-gray-800 border-gray-700 text-center text-white">
              <SelectValue placeholder="Write-up Type" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 text-white border-gray-700">
              <SelectItem value="general">General</SelectItem>
              <SelectItem value="essay">Essay</SelectItem>
              <SelectItem value="report">Report</SelectItem>
              <SelectItem value="case_study">Case Study</SelectItem>
              <SelectItem value="case_scenario">Case Scenario</SelectItem>
              <SelectItem value="dissertation">Dissertation</SelectItem>
              <SelectItem value="reflection">Reflection</SelectItem>
              <SelectItem value="coding">Coding</SelectItem>
              <SelectItem value="presentation">Presentation</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

// Error fallback component
const ErrorFallback: React.FC = () => (
  <div className="w-full max-w-4xl mx-auto p-6">
    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-center">
      <p className="text-red-400">Failed to load input form. Please refresh the page.</p>
    </div>
  </div>
);

// Export wrapped component
export const InputForm: React.FC<InputFormProps> = (props) => (
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <InputFormComponent {...props} />
  </ErrorBoundary>
);
