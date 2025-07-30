import React, { useState } from 'react';
import { Download, FileText, Presentation, Shield, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';

interface DownloadOption {
  type: 'docx' | 'pdf' | 'pptx' | 'csv';
  label: string;
  icon: React.ReactNode;
  url?: string;
  ready: boolean;
  size?: string;
}

interface DownloadMenuProps {
  traceId: string;
  derivatives: { kind: string; url: string }[];
  plagiarismScore?: number;
  qualityScore?: number;
  onDownload?: (type: string) => void;
  onOriginalityCheck?: () => void;
}

export const DownloadMenu: React.FC<DownloadMenuProps> = ({
  traceId,
  derivatives,
  plagiarismScore,
  qualityScore,
  onDownload,
  onOriginalityCheck
}) => {
  const [downloading, setDownloading] = useState<string | null>(null);

  const baseDownloads: DownloadOption[] = [
    {
      type: 'docx',
      label: 'Word Document',
      icon: <FileText className="w-4 h-4" />,
      ready: derivatives.some(d => d.kind === 'docx'),
      url: derivatives.find(d => d.kind === 'docx')?.url
    },
    {
      type: 'pdf',
      label: 'PDF Document',
      icon: <FileText className="w-4 h-4" />,
      ready: derivatives.some(d => d.kind === 'pdf'),
      url: derivatives.find(d => d.kind === 'pdf')?.url
    },
    {
      type: 'pptx',
      label: 'PowerPoint Slides',
      icon: <Presentation className="w-4 h-4" />,
      ready: derivatives.some(d => d.kind === 'slides'),
      url: derivatives.find(d => d.kind === 'slides')?.url
    }
  ];

  const handleDownload = async (option: DownloadOption) => {
    if (!option.ready) return;
    
    setDownloading(option.type);
    
    try {
      if (option.url) {
        // Direct download from derivative URL
        const link = document.createElement('a');
        link.href = option.url;
        link.download = `${traceId}.${option.type}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Fallback to API endpoint
        const response = await fetch(`/api/doc/${traceId}/${option.type}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!response.ok) throw new Error('Download failed');
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${traceId}.${option.type}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
      
      onDownload?.(option.type);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  const getPlagiarismStatus = () => {
    if (plagiarismScore === undefined) return null;
    
    if (plagiarismScore > 15) {
      return {
        icon: <AlertCircle className="w-4 h-4 text-red-400" />,
        text: `${plagiarismScore}% - Review needed`,
        color: 'text-red-400'
      };
    }
    
    return {
      icon: <CheckCircle className="w-4 h-4 text-green-400" />,
      text: `${plagiarismScore}% - Acceptable`,
      color: 'text-green-400'
    };
  };

  const readyCount = baseDownloads.filter(d => d.ready).length;
  const plagiarismStatus = getPlagiarismStatus();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          className="relative bg-gray-800 border-gray-700 text-white hover:bg-gray-700"
          disabled={readyCount === 0}
        >
          <Download className="w-4 h-4 mr-2" />
          Download
          {readyCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 text-white text-xs rounded-full flex items-center justify-center">
              {readyCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-64 bg-gray-800 border-gray-700">
        <div className="p-2 border-b border-gray-700">
          <p className="text-sm font-medium text-white">Available Downloads</p>
          {qualityScore && (
            <p className="text-xs text-gray-400">Quality Score: {qualityScore}%</p>
          )}
        </div>
        
        {baseDownloads.map((option) => (
          <DropdownMenuItem
            key={option.type}
            onClick={() => handleDownload(option)}
            disabled={!option.ready || downloading === option.type}
            className="flex items-center gap-3 p-3 hover:bg-gray-700 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex-shrink-0">
              {downloading === option.type ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                option.icon
              )}
            </div>
            
            <div className="flex-grow">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-white">
                  {option.label}
                </span>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  option.ready 
                    ? 'bg-green-900 text-green-300' 
                    : 'bg-gray-700 text-gray-400'
                }`}>
                  {option.ready ? 'Ready' : 'Processing'}
                </span>
              </div>
              
              {option.size && (
                <p className="text-xs text-gray-400 mt-1">{option.size}</p>
              )}
            </div>
          </DropdownMenuItem>
        ))}
        
        {plagiarismStatus && (
          <>
            <DropdownMenuSeparator className="bg-gray-700" />
            <DropdownMenuItem
              onClick={onOriginalityCheck}
              className="flex items-center gap-3 p-3 hover:bg-gray-700 cursor-pointer"
            >
              <div className="flex-shrink-0">
                <Shield className="w-4 h-4 text-orange-400" />
              </div>
              
              <div className="flex-grow">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-white">
                    Originality Check
                  </span>
                  <span className={`text-xs ${plagiarismStatus.color}`}>
                    {plagiarismStatus.text}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  View detailed analysis
                </p>
              </div>
            </DropdownMenuItem>
          </>
        )}
        
        {readyCount === 0 && (
          <div className="p-4 text-center">
            <div className="flex items-center justify-center gap-2 text-gray-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Generating documents...</span>
            </div>
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};