/**
 * TypeScript types for advanced multimodal content processing
 * Supports audio, video, documents, and structured data
 */

export interface MultimediaInsight {
  type: 'speaker_identification' | 'key_quote' | 'technical_concept' | 'statistical_finding' | 'visual_element';
  content: string;
  confidence: number;
  timestamp?: number; // For audio/video content
  pageNumber?: number; // For document content
  metadata: {
    speaker?: string;
    expertise_area?: string;
    citation_count?: number;
    academic_relevance?: number;
  };
}

export interface ProcessedContent {
  fileId: string;
  fileName: string;
  fileType: 'audio' | 'video' | 'pdf' | 'docx' | 'excel' | 'text' | 'youtube';
  processingStatus: 'completed' | 'processing' | 'error';
  
  // Core content
  chunks: ContentChunk[];
  
  // Extracted insights
  insights: MultimediaInsight[];
  
  // Processing metadata
  processingTime: number;
  tokensGenerated: number;
  qualityScore: number;
  
  // Type-specific content
  audioContent?: AudioProcessingResult;
  videoContent?: VideoProcessingResult;
  documentContent?: DocumentProcessingResult;
  dataContent?: DataProcessingResult;
  
  // Academic integration
  citations: ExtractedCitation[];
  keyFindings: string[];
  academicRelevance: number;
  
  // Integration readiness
  contextIntegrationScore: number;
  embeddings: number[];
}

export interface ContentChunk {
  chunkId: string;
  content: string;
  wordCount: number;
  semanticType: 'introduction' | 'methodology' | 'findings' | 'discussion' | 'conclusion' | 'citation' | 'data';
  importance: number; // 0-1 relevance score
  citations: string[];
  timestamp?: number; // For audio/video
  pageNumber?: number; // For documents
  embeddings: number[];
}

export interface AudioProcessingResult {
  transcription: string;
  speakerSegments: SpeakerSegment[];
  keyQuotes: KeyQuote[];
  audioQuality: number;
  duration: number;
  processingEngine: 'whisper-large-v3' | 'whisper-large-v2';
}

export interface SpeakerSegment {
  speakerId: string;
  speakerName?: string;
  startTime: number;
  endTime: number;
  text: string;
  confidence: number;
  expertiseArea?: string;
  credibilityScore?: number;
}

export interface KeyQuote {
  text: string;
  speaker: string;
  timestamp: number;
  academicRelevance: number;
  citationPotential: number;
  context: string;
}

export interface VideoProcessingResult {
  audioTranscription: AudioProcessingResult;
  visualAnalysis: VisualAnalysisResult;
  slides: ExtractedSlide[];
  charts: ExtractedChart[];
  keyFrames: KeyFrame[];
  duration: number;
  resolution: string;
}

export interface VisualAnalysisResult {
  slideCount: number;
  chartCount: number;
  textExtractions: TextExtraction[];
  academicContent: AcademicVisualContent[];
  geminiAnalysis: string;
}

export interface ExtractedSlide {
  slideNumber: number;
  timestamp: number;
  title?: string;
  content: string;
  visualElements: VisualElement[];
  academicValue: number;
}

export interface ExtractedChart {
  chartType: 'bar' | 'line' | 'pie' | 'scatter' | 'table' | 'flow' | 'other';
  timestamp: number;
  title: string;
  data: ChartDataPoint[];
  insights: string[];
  statisticalSignificance?: number;
}

export interface ChartDataPoint {
  label: string;
  value: number | string;
  category?: string;
}

export interface KeyFrame {
  timestamp: number;
  description: string;
  academicRelevance: number;
  visualElements: VisualElement[];
}

export interface VisualElement {
  type: 'text' | 'chart' | 'diagram' | 'equation' | 'table';
  boundingBox: { x: number; y: number; width: number; height: number };
  content: string;
  confidence: number;
}

export interface TextExtraction {
  text: string;
  confidence: number;
  boundingBox: { x: number; y: number; width: number; height: number };
  fontSize?: number;
  fontWeight?: string;
}

export interface AcademicVisualContent {
  type: 'research_finding' | 'methodology_diagram' | 'statistical_chart' | 'theoretical_model';
  content: string;
  academicValue: number;
  citationPotential: number;
}

export interface DocumentProcessingResult {
  pageCount: number;
  wordCount: number;
  citationCount: number;
  sections: DocumentSection[];
  extractedImages: ExtractedImage[];
  references: ExtractedCitation[];
  agenticDocAnalysis: AgenticDocResult;
}

export interface DocumentSection {
  sectionType: 'title' | 'abstract' | 'introduction' | 'methodology' | 'results' | 'discussion' | 'conclusion' | 'references';
  title: string;
  content: string;
  pageNumbers: number[];
  wordCount: number;
  citationCount: number;
  academicQuality: number;
}

export interface ExtractedImage {
  imageId: string;
  pageNumber: number;
  caption?: string;
  description: string;
  type: 'chart' | 'diagram' | 'photo' | 'equation' | 'table';
  academicRelevance: number;
}

export interface ExtractedCitation {
  citationId: string;
  citationText: string;
  authors: string[];
  title: string;
  journal?: string;
  year: number;
  doi?: string;
  citationStyle: 'APA' | 'MLA' | 'Chicago' | 'Harvard' | 'IEEE';
  pageNumbers: number[];
  contextSentences: string[];
  academicCredibility: number;
}

export interface AgenticDocResult {
  semanticStructure: SemanticStructure;
  researchQuality: number;
  citationAccuracy: number;
  methodologicalSoundness: number;
  originalityScore: number;
  keyContributions: string[];
}

export interface SemanticStructure {
  hierarchicalSections: HierarchicalSection[];
  argumentFlow: ArgumentConnection[];
  evidenceChain: EvidenceLink[];
  conceptualFramework: ConceptualNode[];
}

export interface HierarchicalSection {
  level: number;
  title: string;
  content: string;
  subsections: HierarchicalSection[];
  academicFunction: string;
}

export interface ArgumentConnection {
  fromSection: string;
  toSection: string;
  connectionType: 'support' | 'contrast' | 'extension' | 'application';
  strength: number;
}

export interface EvidenceLink {
  claim: string;
  evidence: string[];
  evidenceType: 'empirical' | 'theoretical' | 'anecdotal' | 'statistical';
  strength: number;
}

export interface ConceptualNode {
  concept: string;
  definition: string;
  relationships: ConceptRelationship[];
  academicDiscipline: string[];
}

export interface ConceptRelationship {
  relatedConcept: string;
  relationshipType: 'is-a' | 'part-of' | 'causes' | 'enables' | 'contradicts';
  strength: number;
}

export interface DataProcessingResult {
  rowCount: number;
  columnCount: number;
  dataTypes: DataColumnInfo[];
  statisticalSummary: StatisticalSummary;
  correlations: CorrelationAnalysis[];
  patterns: DataPattern[];
  visualizations: GeneratedVisualization[];
  economicInsights?: EconomicAnalysis;
}

export interface DataColumnInfo {
  columnName: string;
  dataType: 'numeric' | 'categorical' | 'datetime' | 'text';
  nullCount: number;
  uniqueCount: number;
  sample: any[];
}

export interface StatisticalSummary {
  numericColumns: NumericSummary[];
  categoricalColumns: CategoricalSummary[];
  overallDataQuality: number;
}

export interface NumericSummary {
  columnName: string;
  mean: number;
  median: number;
  stdDev: number;
  min: number;
  max: number;
  quartiles: [number, number, number];
  outliers: number[];
}

export interface CategoricalSummary {
  columnName: string;
  categories: CategoryInfo[];
  mostCommon: string;
  diversity: number;
}

export interface CategoryInfo {
  category: string;
  count: number;
  percentage: number;
}

export interface CorrelationAnalysis {
  column1: string;
  column2: string;
  correlationType: 'pearson' | 'spearman' | 'kendall';
  coefficient: number;
  significance: number;
  interpretation: string;
}

export interface DataPattern {
  patternType: 'trend' | 'seasonality' | 'outlier_cluster' | 'distribution_shift';
  description: string;
  significance: number;
  affectedColumns: string[];
  statisticalEvidence: any;
}

export interface GeneratedVisualization {
  chartType: 'histogram' | 'scatter' | 'line' | 'bar' | 'box' | 'heatmap';
  title: string;
  description: string;
  imageUrl?: string;
  academicValue: number;
  insights: string[];
}

export interface EconomicAnalysis {
  costBenefitMetrics: CostBenefitMetric[];
  roiCalculations: ROICalculation[];
  economicInsights: string[];
  financialProjections: FinancialProjection[];
}

export interface CostBenefitMetric {
  metric: string;
  cost: number;
  benefit: number;
  netValue: number;
  currency: string;
  timeframe: string;
}

export interface ROICalculation {
  scenario: string;
  investment: number;
  returns: number;
  roi: number;
  paybackPeriod: number;
  netPresentValue: number;
}

export interface FinancialProjection {
  year: number;
  projectedValue: number;
  confidence: number;
  assumptions: string[];
}

export interface FileProcessingEvent {
  eventType: 'processing_started' | 'chunk_completed' | 'insight_extracted' | 'processing_completed' | 'processing_error';
  fileId: string;
  fileName: string;
  progress: number;
  stage: string;
  data?: any;
  timestamp: number;
  estimatedCompletion?: number;
}

export interface ContextAssemblyResult {
  assembledContext: string;
  tokenCount: number;
  contextSections: ContextSection[];
  priorityScores: PriorityScore[];
  optimizationReport: OptimizationReport;
}

export interface ContextSection {
  sourceFileId: string;
  sectionType: 'audio_insight' | 'video_analysis' | 'document_chunk' | 'data_finding';
  content: string;
  relevanceScore: number;
  tokenCount: number;
}

export interface PriorityScore {
  fileId: string;
  fileName: string;
  overallScore: number;
  relevanceFactors: RelevanceFactor[];
}

export interface RelevanceFactor {
  factor: 'semantic_similarity' | 'academic_credibility' | 'temporal_relevance' | 'citation_potential';
  score: number;
  weight: number;
}

export interface OptimizationReport {
  originalTokenCount: number;
  optimizedTokenCount: number;
  compressionRatio: number;
  informationRetention: number;
  optimizationTechniques: string[];
}