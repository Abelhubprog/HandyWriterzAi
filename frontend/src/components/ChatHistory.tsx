interface ChatHistoryProps {
  history: any[];
  onSelectConversation: (conversationId: string) => void;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({ history, onSelectConversation }) => {
  return (
    <div className="h-full">
      <div className="p-4 bg-neutral-700 rounded-lg mb-4">
        <h3 className="font-bold text-neutral-100 mb-4">Chat History</h3>
        <div className="space-y-2">
          {history.length === 0 ? (
            <div className="text-center text-neutral-400 py-8">
              No conversations yet
            </div>
          ) : (
            history.map((item) => (
              <div 
                key={item.id} 
                className="p-3 bg-neutral-600 rounded-md cursor-pointer hover:bg-neutral-500 transition-colors"
                onClick={() => onSelectConversation(item.id)}
              >
                <p className="font-medium text-neutral-100 truncate">{item.title}</p>
                <p className="text-xs text-neutral-400 mt-1">{new Date(item.created_at).toLocaleString()}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};