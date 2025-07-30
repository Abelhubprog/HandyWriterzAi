import React from "react";
import { Brain, Zap, FileText, Users, Globe, Shield, Sparkles, ArrowRight } from "lucide-react";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string,
    fileIds: string[]
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
  onExampleClick?: (text: string) => void;
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
  onExampleClick,
}) => {
  const handleExampleCardClick = (prompt: string) => {
    if (onExampleClick) {
      onExampleClick(prompt);
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-8 py-12 bg-gray-900">
      {/* YC Demo Examples - Clean and focused */}
      <div className="w-full max-w-4xl">
        <h2 className="text-2xl font-semibold text-gray-200 mb-8">
          ✨ YC Demo Examples
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {YCDemoExamples.map((example, index) => {
            const Icon = example.icon;
            return (
              <div
                key={index}
                className={`relative p-6 rounded-xl border border-gray-700 bg-gradient-to-br ${example.gradient} backdrop-blur-sm hover:border-gray-600 hover:scale-[1.02] transition-all duration-200 group cursor-pointer`}
                onClick={() => handleExampleCardClick(example.prompt)}
              >
                <div className="flex items-center gap-3 mb-3">
                  <Icon className="h-6 w-6 text-white" />
                  <h3 className="text-lg font-semibold text-white">{example.title}</h3>
                </div>
                <p className="text-gray-300 text-sm mb-3 leading-relaxed">{example.description}</p>
                <div className="flex items-center gap-2 text-blue-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  <span>Try this example</span>
                  <ArrowRight className="h-4 w-4" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
