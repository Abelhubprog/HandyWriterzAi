import React from 'react';
import { Plus, Camera, Image as ImageIcon, File as FileIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const MAX_FILES = 50;
const MAX_SIZE = 100 * 1024 * 1024; // 100 MB

function toast(msg: string) {
  const t = document.createElement('div');
  t.className = 'fixed top-4 right-4 bg-black/80 text-white px-3 py-1 rounded';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2000);
}

import * as tus from "tus-js-client";

async function sendToAgents(files: File[]) {
  for (const file of files) {
    const upload = new tus.Upload(file, {
      endpoint: "/api/files",
      retryDelays: [0, 3000, 5000, 10000, 20000],
      metadata: {
        filename: file.name,
        filetype: file.type,
      },
      onError: (error) => {
        console.log("Failed because: " + error);
        toast(`Error: ${error}`);
      },
      onProgress: (bytesUploaded, bytesTotal) => {
        const percentage = ((bytesUploaded / bytesTotal) * 100).toFixed(2);
        console.log(bytesUploaded, bytesTotal, percentage + "%");
      },
      onSuccess: () => {
        console.log("Download %s from %s", upload.file.name, upload.url);
        toast("Files uploaded successfully!");
      },
    });

    // Start the upload
    upload.start();
  }
}

export const ContextUploadMenu: React.FC = () => {
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const k2Pick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    if (files.length === 0) return;

    if (files.length > MAX_FILES) {
      return toast(`Error: Cannot select more than ${MAX_FILES} files.`);
    }

    for (const file of files) {
      if (file.size > MAX_SIZE) {
        return toast(`Error: File "${file.name}" exceeds the ${MAX_SIZE / (1024 * 1024)}MB size limit.`);
      }
    }

    toast(`📎 ${files.length} file(s)`);

    // chunk + embed + store
    await sendToAgents(files);
  };

  return (
    <>
      <input
        id="k2-file"
        type="file"
        multiple
        style={{ display: 'none' }}
        accept="*"
        ref={fileInputRef}
        onChange={handleFileChange}
      />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8"
          >
            <Plus className="h-5 w-5" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem onClick={k2Pick}>
            <ImageIcon className="mr-2 h-4 w-4" />
            <span>Add photos & files</span>
          </DropdownMenuItem>
          <DropdownMenuItem disabled>
            <Camera className="mr-2 h-4 w-4" />
            <span>Take photo</span>
          </DropdownMenuItem>
          <DropdownMenuItem disabled>
            <FileIcon className="mr-2 h-4 w-4" />
            <span>Take screenshot</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  );
};
