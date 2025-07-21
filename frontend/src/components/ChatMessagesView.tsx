import { Message } from "@langchain/langgraph-sdk";
import { InputForm } from "./InputForm";
import { AgentActivityStream } from "./AgentActivityStream";
import { ProcessedEvent } from "./ActivityTimeline";
import { ScrollArea } from "./ui/scroll-area";
import { DownloadMenu } from "./DownloadMenu";
import { TimelineEvent } from "@/hooks/useStream";

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement>;
  onSubmit: (inputValue: string, writeupType: string, model: string, fileIds: string[]) => void;
  onCancel: () => void;
  liveActivityEvents: TimelineEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
  traceId?: string | null;
  totalCost?: number;
  plagiarismScore?: number;
  qualityScore?: number;
  derivatives?: { kind: string; url: string }[];
}

export const ChatMessagesView: React.FC<ChatMessagesViewProps> = ({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  liveActivityEvents,
  historicalActivities,
  traceId,
  totalCost,
  plagiarismScore,
  qualityScore,
  derivatives = [],
}) => {
  return (
    <div className="h-full flex flex-col bg-gray-900">
      <ScrollArea className="flex-grow p-6" ref={scrollAreaRef}>
        <div className="space-y-6 max-w-4xl mx-auto">
          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.type === 'human' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${msg.type === 'human' ? 'ml-auto' : 'mr-auto'}`}>
                <div className={`p-4 rounded-2xl ${
                  msg.type === 'human' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-800 text-gray-100 border border-gray-700'
                }`}>
                  <div className="whitespace-pre-wrap break-words">
                    {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                  </div>
                  {msg.type === 'ai' && traceId && derivatives.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-600">
                      <DownloadMenu
                        traceId={traceId}
                        derivatives={derivatives}
                        plagiarismScore={plagiarismScore}
                        qualityScore={qualityScore}
                        onOriginalityCheck={() => {
                          // Navigate to originality workbench
                          window.open(`/originality/${traceId}`, '_blank');
                        }}
                      />
                    </div>
                  )}
                </div>
                {msg.type === 'human' && (
                  <div className="text-xs text-gray-400 mt-1 text-right">
                    You
                  </div>
                )}
                {msg.type === 'ai' && (
                  <div className="text-xs text-gray-400 mt-1">
                    HandyWriterz
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
      {isLoading && (
        <div className="border-t border-gray-700 bg-gray-800/50">
          <AgentActivityStream 
            events={liveActivityEvents}
            totalCost={totalCost}
            plagiarismScore={plagiarismScore}
            qualityScore={qualityScore}
            derivatives={derivatives}
          />
        </div>
      )}
      <div className="border-t border-gray-700 bg-gray-900">
        <InputForm
          onSubmit={onSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={messages.length > 0}
        />
      </div>
    </div>
  );
};
