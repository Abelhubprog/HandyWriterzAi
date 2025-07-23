import React from "react";
import { InputForm } from "./InputForm";
import { Brain, Zap, FileText, Users, Globe, Shield, Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string,
    fileIds: string[]
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const YCDemoExamples = [
  {
    title: "PhD Dissertation",
    description: "10 files → Complete dissertation",
    prompt: "Create a comprehensive PhD dissertation on 'AI-Powered Educational Technology Impact' using the uploaded literature review, methodology, interview transcripts, statistical analysis, and supporting materials.",
    icon: FileText,
    gradient: "from-blue-500/20 to-purple-500/20"
  },
  {
    title: "Market Research",
    description: "Industry analysis → Strategic insights",
    prompt: "Conduct comprehensive market analysis of the EdTech sector, focusing on AI integration trends, competitive landscape, and growth opportunities for a Series A startup.",
    icon: Globe,
    gradient: "from-green-500/20 to-teal-500/20"
  },
  {
    title: "Technical Report",
    description: "Complex data → Clear conclusions",
    prompt: "Generate a technical report analyzing machine learning model performance across different educational contexts, including statistical validation and implementation recommendations.",
    icon: Brain,
    gradient: "from-orange-500/20 to-red-500/20"
  }
];

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => (
  <div className="h-full flex flex-col items-center justify-center text-center px-6 flex-1 w-full max-w-6xl mx-auto">
    {/* Hero Section */}
    <div className="mb-12 space-y-6">
      <div className="flex items-center justify-center gap-3 mb-4">
        <div className="relative">
          <Brain className="h-12 w-12 text-blue-400" />
          <Sparkles className="h-6 w-6 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
        </div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
          HandyWriterz
        </h1>
      </div>
      
      <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
        The world's most advanced AI-powered academic writing platform. 
        <span className="text-blue-400 font-medium"> 30+ specialized agents</span> working together 
        to transform your research into publication-ready content.
      </p>
      
      <div className="flex items-center justify-center gap-8 text-sm text-gray-400">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-yellow-400" />
          <span>Multimodal Processing</span>
        </div>
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-green-400" />
          <span>Agent Orchestration</span>
        </div>
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-blue-400" />
          <span>Academic Integrity</span>
        </div>
      </div>
    </div>

    {/* YC Demo Examples */}
    <div className="mb-8 w-full">
      <h2 className="text-2xl font-semibold text-gray-200 mb-6">
        ✨ YC Demo Examples
      </h2>
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {YCDemoExamples.map((example, index) => {
          const Icon = example.icon;
          return (
            <div
              key={index}
              className={`relative p-6 rounded-xl border border-gray-700 bg-gradient-to-br ${example.gradient} backdrop-blur-sm hover:border-gray-600 transition-all duration-300 group cursor-pointer`}
              onClick={() => {
                const textarea = document.querySelector('textarea');
                if (textarea) {
                  textarea.value = example.prompt;
                  textarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
              }}
            >
              <div className="flex items-center gap-3 mb-3">
                <Icon className="h-6 w-6 text-white" />
                <h3 className="font-semibold text-white">{example.title}</h3>
              </div>
              <p className="text-gray-300 text-sm mb-3">{example.description}</p>
              <div className="flex items-center gap-2 text-blue-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Try this example</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </div>
          );
        })}
      </div>
    </div>

    {/* Main Input Form */}
    <div className="w-full">
      <InputForm
        onSubmit={handleSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={false}
      />
    </div>
    
    {/* Footer */}
    <div className="mt-8 text-center">
      <p className="text-sm text-gray-500">
        Powered by <span className="text-blue-400">Gemini 2.5 Pro</span>, 
        <span className="text-green-400"> Claude Sonnet</span>, and 
        <span className="text-purple-400"> GPT-4</span>
      </p>
      <p className="text-xs text-gray-600 mt-2">
        Ready for production • CPU optimized • Zero-cost deployment
      </p>
    </div>
  </div>
);
