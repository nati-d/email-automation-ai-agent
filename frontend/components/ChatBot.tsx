"use client"

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { MessageCircle, X, Send, Bot, User, Minimize2, Maximize2, Sparkles } from 'lucide-react';
import { sendChatBotMessage, type ChatBotMessage } from '@/lib/api/email';
import { useApp } from '@/components/AppContext';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export default function ChatBot() {
  const { user } = useApp();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI email assistant. I can help you manage emails, draft responses, analyze sentiment, and organize your inbox. How can I assist you today?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const payload: ChatBotMessage = {
        message: inputValue,
      };

      const response = await sendChatBotMessage(payload);
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message to chatbot:', error);
      
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        sender: 'bot',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMaximize = () => {
    setIsMaximized(!isMaximized);
    setIsMinimized(false);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="group relative h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 bg-primary hover:bg-primary/90 text-primary-foreground border-0"
        >
          <MessageCircle className="w-6 h-6 transition-transform group-hover:scale-110" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full animate-pulse"></div>
        </Button>
      </div>
    );
  }

  return (
    <div className={`fixed z-50 transition-all duration-300 ${
      isMaximized 
        ? 'inset-0 p-4' 
        : 'bottom-6 right-6'
    }`}>
      <Card className={`shadow-2xl border-0 bg-card/95 backdrop-blur-sm transition-all duration-300 ${
        isMaximized 
          ? 'w-full h-full flex flex-col' 
          : isMinimized 
            ? 'w-96 h-auto' 
            : 'w-96 h-[500px]'
      }`}>
        <CardHeader className={`flex flex-row items-center justify-between pt-4 space-y-0 pb-3 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground ${
          isMinimized ? 'rounded-xl border-0' : 'rounded-t-xl border-b'
        } ${isMaximized ? 'flex-shrink-0' : ''}`}>
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-foreground/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">AI Email Assistant</h3>
              <p className="text-xs text-primary-foreground/80">Powered by AI</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
           
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMaximize}
              className="h-8 w-8 p-0 text-primary-foreground hover:bg-primary-foreground/20 transition-colors"
              title={isMaximized ? "Restore chat" : "Maximize chat"}
            >
              <Maximize2 className={`w-4 h-4 ${isMaximized ? 'rotate-180' : ''}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 p-0 text-primary-foreground hover:bg-primary-foreground/20 transition-colors"
              title="Close chat"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>

        <div className={`transition-all duration-300 overflow-hidden ${
          isMinimized 
            ? 'max-h-0 opacity-0' 
            : isMaximized 
              ? 'flex-1 flex flex-col opacity-100' 
              : 'max-h-[500px] opacity-100'
        }`}>
          <CardContent className={`p-0 overflow-hidden ${isMaximized ? 'flex-1 flex flex-col' : 'flex-1'}`}>
            <div className={`overflow-y-auto p-4 space-y-4 hide-scrollbar ${
              isMaximized ? 'flex-1' : 'h-[380px]'
            }`}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`${isMaximized ? 'max-w-[70%]' : 'max-w-[85%]'} rounded-2xl px-4 py-3 shadow-sm ${
                      message.sender === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground border border-border'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {message.sender === 'bot' && (
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center">
                          <Bot className="w-3 h-3 text-accent" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className={`leading-relaxed break-words ${isMaximized ? 'text-base' : 'text-sm'}`}>
                          {message.text}
                        </p>
                        <p className={`text-xs mt-2 ${
                          message.sender === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground/60'
                        }`}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                      {message.sender === 'user' && (
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                          <User className="w-3 h-3 text-primary-foreground" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl px-4 py-3 border border-border">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center">
                        <Bot className="w-3 h-3 text-accent" />
                      </div>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </CardContent>

          <CardFooter className={`p-4 border-t bg-muted/30 ${isMaximized ? 'flex-shrink-0' : ''}`}>
            <div className="flex gap-3 w-full">
              <Input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className={`flex-1 border-border bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary ${
                  isMaximized ? 'text-base h-12' : 'text-sm'
                }`}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                size="sm"
                className={`bg-primary hover:bg-primary/90 text-primary-foreground border-0 p-0 ${
                  isMaximized ? 'h-12 w-12' : 'h-10 w-10'
                }`}
              >
                <Send className={`${isMaximized ? 'w-5 h-5' : 'w-4 h-4'}`} />
              </Button>
            </div>
          </CardFooter>
        </div>
      </Card>
    </div>
  );
} 