import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare, X, Send, Loader2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() && !isLoading) {
      const userMessage: Message = { role: 'user', content: input };
      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const response = await fetch('http://localhost:8088/chat', { // Assuming chat agent runs on 8088
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: input,
            history: messages,
          }),
        });

        if (!response.body) {
          throw new Error('No response body');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage: Message = { role: 'assistant', content: '' };
        setMessages((prev) => [...prev, assistantMessage]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          setMessages((prev) =>
            prev.map((msg, index) =>
              index === prev.length - 1
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        }
      } catch (error) {
        console.error('Error fetching chat response:', error);
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: 'Sorry, something went wrong.' },
        ]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <>
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-8 right-8 rounded-full w-16 h-16 shadow-xl z-50 bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 backdrop-blur-sm border border-stone-400/40"
      >
        {isOpen ? <X className="w-6 h-6 text-white" /> : <MessageSquare className="w-6 h-6 text-white" />}
      </Button>

      {isOpen && (
        <Card className="fixed bottom-28 right-8 w-96 h-[600px] flex flex-col shadow-2xl z-50 bg-white/25 backdrop-blur-lg border border-stone-400/40">
          <CardHeader className="flex flex-row items-center justify-between bg-white/15 backdrop-blur-sm border-b border-stone-400/30">
            <CardTitle className="text-stone-900 font-bold">Chat with our AI</CardTitle>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setIsOpen(false)}
              className="hover:bg-white/20 text-stone-700 hover:text-stone-900"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent className="flex-grow p-4">
            <ScrollArea className="h-full pr-4" ref={scrollAreaRef}>
              <div className="flex flex-col space-y-4">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex items-end ${
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`px-4 py-2 rounded-lg max-w-xs ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-r from-green-800 to-green-900 text-white shadow-lg backdrop-blur-sm'
                          : 'bg-white/40 backdrop-blur-sm text-stone-800 border border-stone-400/30'
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-end justify-start">
                    <div className="px-4 py-2 rounded-lg max-w-xs bg-white/40 backdrop-blur-sm border border-stone-400/30">
                      <Loader2 className="h-5 w-5 animate-spin text-green-800" />
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
          <CardFooter className="bg-white/15 backdrop-blur-sm border-t border-stone-400/30">
            <div className="flex w-full items-center space-x-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type a message..."
                disabled={isLoading}
                className="bg-white/40 backdrop-blur-sm border border-stone-400/50 text-stone-800 placeholder-stone-600"
              />
              <Button 
                onClick={handleSendMessage} 
                disabled={isLoading}
                className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardFooter>
        </Card>
      )}
    </>
  );
} 