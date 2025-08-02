"use client";

import React, { useState, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Eye,
  Camera,
  Upload,
  Scan,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  FileText,
  Highlighter,
  Zap
} from 'lucide-react';
import { toast } from '@/components/ui/use-toast';

interface HighlightedSection {
  id: string;
  text: string;
  coordinates: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  issueType: 'similarity' | 'ai_detection' | 'grammar' | 'citation' | 'other';
  severity: 'high' | 'medium' | 'low';
  suggestion?: string;
}

interface VisionAnalysisResult {
  documentId: string;
  highlightedSections: HighlightedSection[];
  overallScore: {
    similarityScore: number;
    aiScore: number;
    grammarScore: number;
  };
  agentRecommendations: string[];
  processingTime: number;
}

interface VisionAnalyzerProps {
  documentId: string;
  onAnalysisComplete: (result: VisionAnalysisResult) => void;
  onSectionRewrite: (sectionId: string, originalText: string) => void;
}

export function VisionAnalyzer({ documentId, onAnalysisComplete, onSectionRewrite }: VisionAnalyzerProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<VisionAnalysisResult | null>(null);
  const [selectedSection, setSelectedSection] = useState<HighlightedSection | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const validFiles = files.filter(file => 
      file.type.includes('image/') || file.type.includes('pdf')
    );

    if (validFiles.length !== files.length) {
      toast({
        title: "Invalid File Type",
        description: "Please upload only image files (PNG, JPG, PDF) with highlighted sections.",
        variant: "destructive"
      });
    }

    setUploadedFiles(prev => [...prev, ...validFiles]);
  }, []);

  const removeFile = useCallback((index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const performVisionAnalysis = async () => {
    if (uploadedFiles.length === 0) {
      toast({
        title: "No Files Selected",
        description: "Please upload at least one image or PDF with highlighted sections.",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      // Simulate advanced vision processing
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Mock vision analysis result with highlighted sections detection
      const mockHighlightedSections: HighlightedSection[] = [
        {
          id: 'section-1',
          text: 'This particular implementation of machine learning algorithms shows significant overlap with existing research methodologies.',
          coordinates: { x: 120, y: 450, width: 480, height: 60 },
          confidence: 0.92,
          issueType: 'similarity',
          severity: 'high',
          suggestion: 'Consider paraphrasing and adding original analysis to reduce similarity.'
        },
        {
          id: 'section-2', 
          text: 'The methodology employed in this study utilizes advanced statistical techniques for data analysis.',
          coordinates: { x: 150, y: 680, width: 420, height: 40 },
          confidence: 0.87,
          issueType: 'ai_detection',
          severity: 'medium',
          suggestion: 'This section may need human touch to reduce AI detection patterns.'
        },
        {
          id: 'section-3',
          text: 'Research findings indicates that there is a correlation between variables.',
          coordinates: { x: 180, y: 920, width: 380, height: 35 },
          confidence: 0.95,
          issueType: 'grammar',
          severity: 'low',
          suggestion: 'Grammar correction: "findings indicate" not "findings indicates".'
        }
      ];

      const result: VisionAnalysisResult = {
        documentId,
        highlightedSections: mockHighlightedSections,
        overallScore: {
          similarityScore: 18,
          aiScore: 25,
          grammarScore: 95
        },
        agentRecommendations: [
          'Rewrite section-1 to reduce similarity with existing sources',
          'Enhance section-2 with more human-like expressions and personal insights',
          'Fix grammatical error in section-3',
          'Consider adding more original analysis throughout the document'
        ],
        processingTime: 2850
      };

      setAnalysisResult(result);
      onAnalysisComplete(result);

      toast({
        title: "Vision Analysis Complete",
        description: `Identified ${mockHighlightedSections.length} highlighted sections for review.`,
      });

    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: "Failed to analyze the uploaded documents. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSectionRewrite = (section: HighlightedSection) => {
    onSectionRewrite(section.id, section.text);
    toast({
      title: "Section Sent for Rewrite",
      description: "The highlighted section has been sent to the AI agent for rewriting.",
    });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500'; 
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getIssueTypeIcon = (issueType: string) => {
    switch (issueType) {
      case 'similarity': return <Scan className="w-4 h-4" />;
      case 'ai_detection': return <Zap className="w-4 h-4" />;
      case 'grammar': return <FileText className="w-4 h-4" />;
      case 'citation': return <FileText className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* File Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Eye className="w-5 h-5 mr-2" />
            Vision-Based Document Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Alert>
              <Camera className="h-4 w-4" />
              <AlertDescription>
                Upload images or PDFs of the document with highlighted sections that need attention.
                Our AI vision system will automatically detect and analyze the highlighted areas.
              </AlertDescription>
            </Alert>

            {/* File Upload Area */}
            <div 
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Click to upload highlighted document images or drag and drop
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Supports PNG, JPG, PDF files up to 10MB each
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,.pdf"
              multiple
              onChange={handleFileUpload}
              className="hidden"
            />

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Uploaded Files:</h4>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{file.name}</span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeFile(index)}
                    >
                      ×
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Analysis Button */}
            <Button
              onClick={performVisionAnalysis}
              disabled={uploadedFiles.length === 0 || isAnalyzing}
              className="w-full"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing Highlights...
                </>
              ) : (
                <>
                  <Scan className="w-4 h-4 mr-2" />
                  Start Vision Analysis
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-500" />
                Analysis Results
              </span>
              <Badge variant="outline">
                {analysisResult.processingTime}ms
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Overall Scores */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-2xl font-bold text-red-600">
                    {analysisResult.overallScore.similarityScore}%
                  </div>
                  <div className="text-sm text-gray-600">Similarity</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-2xl font-bold text-yellow-600">
                    {analysisResult.overallScore.aiScore}%
                  </div>
                  <div className="text-sm text-gray-600">AI Detection</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded">  
                  <div className="text-2xl font-bold text-green-600">
                    {analysisResult.overallScore.grammarScore}%
                  </div>
                  <div className="text-sm text-gray-600">Grammar</div>
                </div>
              </div>

              {/* Highlighted Sections */}
              <div>
                <h4 className="text-lg font-semibold mb-4">Detected Highlighted Sections</h4>
                <div className="space-y-3">
                  {analysisResult.highlightedSections.map((section) => (
                    <div key={section.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getIssueTypeIcon(section.issueType)}
                          <Badge variant="outline" className="capitalize">
                            {section.issueType.replace('_', ' ')}
                          </Badge>
                          <Badge className={getSeverityColor(section.severity)}>
                            {section.severity}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            {Math.round(section.confidence * 100)}% confidence
                          </span>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => handleSectionRewrite(section)}
                          className="flex items-center"
                        >
                          <RefreshCw className="w-3 h-3 mr-1" />
                          Rewrite
                        </Button>
                      </div>
                      
                      <div className="mb-2">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Highlighted Text:
                        </p>
                        <p className="text-sm bg-yellow-100 dark:bg-yellow-900 p-2 rounded italic">
                          "{section.text}"
                        </p>
                      </div>

                      {section.suggestion && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Suggestion:
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {section.suggestion}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Agent Recommendations */}
              <div>
                <h4 className="text-lg font-semibold mb-4">AI Agent Recommendations</h4>
                <div className="space-y-2">
                  {analysisResult.agentRecommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        {recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}