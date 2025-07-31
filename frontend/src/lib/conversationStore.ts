// Local storage-based conversation management
export interface StoredConversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string;
  messages: any[];
}

export class ConversationStore {
  private static STORAGE_KEY = 'handywriterz_conversations';
  
  static getAllConversations(): StoredConversation[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }
  
  static saveConversation(conversation: StoredConversation): void {
    const conversations = this.getAllConversations();
    const existingIndex = conversations.findIndex(c => c.id === conversation.id);
    
    if (existingIndex >= 0) {
      conversations[existingIndex] = conversation;
    } else {
      conversations.unshift(conversation);
    }
    
    // Keep only the last 50 conversations
    if (conversations.length > 50) {
      conversations.splice(50);
    }
    
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(conversations));
  }
  
  static getConversation(id: string): StoredConversation | null {
    const conversations = this.getAllConversations();
    const conversation = conversations.find(c => c.id === id);
    
    if (conversation && conversation.messages) {
      // Ensure timestamps are properly formatted
      conversation.messages = conversation.messages.map(msg => ({
        ...msg,
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : new Date(msg.timestamp).toISOString()
      }));
    }
    
    return conversation || null;
  }
  
  static deleteConversation(id: string): void {
    const conversations = this.getAllConversations();
    const filtered = conversations.filter(c => c.id !== id);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
  }
  
  static updateConversationTitle(id: string, title: string): void {
    const conversations = this.getAllConversations();
    const conversation = conversations.find(c => c.id === id);
    if (conversation) {
      conversation.title = title;
      conversation.updated_at = new Date().toISOString();
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(conversations));
    }
  }
  
  static updateConversationWithMessage(id: string, messages: any[]): void {
    const conversation = this.getConversation(id);
    if (conversation) {
      // Ensure all timestamps are strings for JSON serialization
      conversation.messages = messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp instanceof Date ? msg.timestamp.toISOString() : msg.timestamp
      }));
      conversation.message_count = messages.length;
      conversation.updated_at = new Date().toISOString();
      
      // Update preview with last message (check for both 'human' and 'user' role)
      const lastUserMessage = messages.filter(m => m.type === 'human' || m.role === 'user').pop();
      if (lastUserMessage) {
        conversation.last_message_preview = typeof lastUserMessage.content === 'string' 
          ? lastUserMessage.content.slice(0, 100) 
          : 'New message';
      }
      
      this.saveConversation(conversation);
    }
  }
  
  static createNewConversation(id: string, firstMessage?: any): StoredConversation {
    const title = firstMessage && typeof firstMessage.content === 'string' 
      ? firstMessage.content.slice(0, 50) + (firstMessage.content.length > 50 ? '...' : '')
      : 'New conversation';
      
    const conversation: StoredConversation = {
      id,
      title,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      message_count: firstMessage ? 1 : 0,
      last_message_preview: firstMessage && typeof firstMessage.content === 'string' 
        ? firstMessage.content.slice(0, 100) 
        : '',
      messages: firstMessage ? [{
        ...firstMessage,
        timestamp: firstMessage.timestamp instanceof Date ? firstMessage.timestamp.toISOString() : firstMessage.timestamp
      }] : [],
    };
    
    this.saveConversation(conversation);
    return conversation;
  }
}