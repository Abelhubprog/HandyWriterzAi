"use client";

import { useState, useEffect } from "react";
import { useStream } from "@/hooks/useStream";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Download } from "lucide-react";

export function DownloadMenu({ traceId }: { traceId: string | null }) {
  const { timeline } = useStream(traceId);
  const [downloads, setDownloads] = useState<{ kind: string; url: string }[]>([]);

  useEffect(() => {
    const newDownloads = timeline
      .filter((event) => event.type === "derivative_ready" || event.type === "format_done")
      .map((event) => ({
        kind: event.kind || (event.type === "format_done" ? "document" : "unknown"),
        url: event.url,
      }));
    setDownloads(newDownloads);
  }, [timeline]);

  if (downloads.length === 0) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Download className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {downloads.map((download, index) => (
          <DropdownMenuItem key={index} asChild>
            <a href={download.url} target="_blank" rel="noopener noreferrer">
              Download {download.kind}
            </a>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
