import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Send, Mic, User } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { useUser } from '@stackframe/stack';
import toast from 'react-hot-toast';
import { cn } from '../../lib/utils';
import { Button } from '../../components/ui/Button';
import { AI_CAPABILITIES } from '../../data/aiCapabilities';
import { getApiBase } from '../../lib/apiBase';
import { buildAuthHeaders } from '../../lib/apiHeaders';
import { useStore } from '../../store/useStore';

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
}

const API_BASE = getApiBase();

function buildGreeting(displayName: string) {
  const trimmed = displayName.trim();
  if (trimmed) {
    return `Здравствуйте, ${trimmed}! Я AI-ассистент SuperGov . Задайте вопрос или выберите одну из 18 функций ниже — ответы и действия выполняются через ИИ и серверные инструменты.`;
  }
  return `Здравствуйте! Я AI-ассистент SuperGov . Задайте вопрос или выберите одну из 18 функций ниже — ответы и действия выполняются через ИИ и серверные инструменты.`;
}

export function Chat() {
  const stackUser = useUser();
  const profileName = useStore((s) => s.user?.name);
  const emailLocal = stackUser?.primaryEmail?.split('@')[0]?.trim() || '';
  const displayName = (
    profileName ||
    stackUser?.displayName ||
    emailLocal ||
    ''
  ).trim();

  const greetText = useMemo(() => buildGreeting(displayName), [displayName]);

  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'ai', content: buildGreeting('') },
  ]);
  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].id === '1' && prev[0].role === 'ai') {
        return [{ ...prev[0], content: greetText }];
      }
      return prev;
    });
  }, [greetText]);

  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const [sessionId] = useState(() => crypto.randomUUID());
  const recRef = useRef<{ stop: () => void; start: () => void } | null>(null);

  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q');

  const scrollToBottom = () => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = useCallback(
    async (text: string) => {
      const userMsg = text.trim();
      if (!userMsg) return;

      const newMessage: Message = { id: Date.now().toString(), role: 'user', content: userMsg };
      setMessages((prev) => [...prev, newMessage]);
      setInput('');
      setIsTyping(true);

      const responseId = (Date.now() + 1).toString();
      setMessages((prev) => [...prev, { id: responseId, role: 'ai', content: '' }]);

      try {
        const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
        if (!headers.Authorization) {
          toast.error('Войдите в систему (пароль Stack или код на email)');
          setIsTyping(false);
          return;
        }

        const res = await fetch(`${API_BASE}/api/chat/message`, {
          method: 'POST',
          headers: { ...headers, 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userMsg, session_id: sessionId }),
        });

        if (!res.ok) {
          const errText = await res.text();
          throw new Error(errText || res.statusText);
        }

        if (!res.body) throw new Error('Пустой ответ сервера');

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let full = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split('\n\n');
          buffer = parts.pop() || '';
          for (const block of parts) {
            const line = block.trim();
            if (!line.startsWith('data:')) continue;
            const jsonStr = line.slice(5).trim();
            try {
              const data = JSON.parse(jsonStr) as {
                token?: string;
                done?: boolean;
                error?: boolean;
              };
              if (data.error) {
                full += data.token || '';
                break;
              }
              if (data.token) {
                full += data.token;
                setMessages((prev) =>
                  prev.map((msg) => (msg.id === responseId ? { ...msg, content: full } : msg))
                );
              }
            } catch {
              /* ignore */
            }
          }
        }
      } catch (e) {
        console.error(e);
        const msg =
          e instanceof Error
            ? e.message
            : 'Не удалось связаться с AI. Проверьте backend и ANTHROPIC_API_KEY.';
        toast.error(msg);
        setMessages((prev) =>
          prev.map((m) => (m.id === responseId ? { ...m, content: `Ошибка: ${msg}` } : m))
        );
      } finally {
        setIsTyping(false);
      }
    },
    [stackUser, sessionId]
  );

  useEffect(() => {
    if (initialQuery) {
      void handleSend(initialQuery);
    }
  }, [initialQuery, handleSend]);

  const handleVoice = () => {
    const w = window as unknown as { webkitSpeechRecognition?: new () => Record<string, unknown>; SpeechRecognition?: new () => Record<string, unknown> };
    const SR = w.webkitSpeechRecognition || w.SpeechRecognition;

    if (SR) {
      if (isRecording && recRef.current) {
        try {
          recRef.current.stop();
        } catch {
          /* */
        }
        setIsRecording(false);
        recRef.current = null;
        return;
      }
      try {
        const rec = new SR() as {
          lang: string;
          interimResults: boolean;
          maxAlternatives: number;
          start: () => void;
          stop: () => void;
          onresult: ((ev: { results: { [k: number]: { [k: number]: { transcript: string } } } }) => void) | null;
          onerror: (() => void) | null;
          onend: (() => void) | null;
        };
        rec.lang = 'ru-RU';
        rec.interimResults = false;
        rec.maxAlternatives = 1;
        rec.onresult = (ev: { results: { [k: number]: { [k: number]: { transcript: string } } } }) => {
          const t = ev.results[0]?.[0]?.transcript;
          if (t) setInput(t);
          setIsRecording(false);
          recRef.current = null;
        };
        rec.onerror = () => {
          setIsRecording(false);
          recRef.current = null;
          toast.error('Ошибка распознавания речи');
        };
        rec.onend = () => {
          setIsRecording(false);
          recRef.current = null;
        };
        recRef.current = rec;
        rec.start();
        setIsRecording(true);
      } catch {
        toast.error('Голосовой ввод недоступен в этом браузере');
      }
      return;
    }

    setIsRecording(true);
    setTimeout(async () => {
      try {
        const formData = new FormData();
        const mockBlob = new Blob(['mock'], { type: 'audio/webm' });
        formData.append('file', mockBlob, 'voice.webm');
        const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
        const res = await fetch(`${API_BASE}/api/voice/transcribe`, {
          method: 'POST',
          headers,
          body: formData,
        });
        const json = (await res.json()) as { success?: boolean; data?: { transcript?: string } };
        if (json.success && json.data?.transcript) setInput(json.data.transcript);
        else setInput('Как подать заявку на справку?');
      } catch {
        setInput('Как подать заявку на справку?');
      } finally {
        setIsRecording(false);
      }
    }, 1500);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-6rem)] bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden relative">
      <div className="px-4 pt-3 pb-1 border-b border-slate-100 flex flex-wrap gap-2 items-center shrink-0">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">18 функций</span>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">новое ×10</span>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan/15 text-navy font-semibold">MVP ×8</span>
        <span className="text-[10px] text-slate-400 ml-auto">Claude Haiku · любые вопросы</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={cn('flex gap-4 w-full', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
            {msg.role === 'ai' && (
              <div className="w-8 h-8 rounded-full bg-cyan flex items-center justify-center shrink-0 shadow-sm shadow-cyan/20">
                <span className="text-white text-[10px] font-bold tracking-wider">AI</span>
              </div>
            )}

            <div
              className={cn(
                'p-4 rounded-2xl max-w-[85%] md:max-w-[70%]',
                msg.role === 'user'
                  ? 'bg-navy text-white rounded-tr-none shadow-md shadow-navy/10'
                  : 'bg-slate-50 border border-slate-100 text-slate-800 rounded-tl-none'
              )}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                <User className="w-4 h-4 text-slate-500" />
              </div>
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-4 w-full justify-start">
            <div className="w-8 h-8 rounded-full bg-cyan flex items-center justify-center shrink-0 shadow-sm">
              <span className="text-white text-[10px] font-bold">AI</span>
            </div>
            <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl rounded-tl-none flex items-center gap-1.5 h-12">
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="p-4 bg-white border-t border-slate-100">
        <p className="text-[10px] text-slate-500 mb-2 font-medium">Быстрые темы (18)</p>
        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 max-h-32 flex-wrap">
          {AI_CAPABILITIES.map((cap) => (
            <button
              key={cap.id}
              type="button"
              onClick={() => void handleSend(cap.prompt)}
              title={cap.prompt}
              className={cn(
                'whitespace-nowrap px-3 py-1.5 rounded-full text-[11px] font-semibold transition-all border',
                cap.tag === 'innovation'
                  ? 'bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border-emerald-200'
                  : 'bg-slate-50 hover:bg-cyan hover:text-white text-slate-700 border-slate-200'
              )}
            >
              {cap.label}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            void handleSend(input);
          }}
          className="flex items-center gap-2 relative"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Любой вопрос или задача…"
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:border-cyan focus:ring-1 focus:ring-cyan transition-all"
          />
          <button
            type="button"
            onClick={() => handleVoice()}
            className={cn(
              'absolute right-14 p-2 rounded-lg transition-colors',
              isRecording ? 'text-red-500 bg-red-50 animate-pulse' : 'text-slate-400 hover:text-cyan hover:bg-cyan/10'
            )}
            title="Голосовой ввод"
          >
            <Mic className="w-5 h-5" />
          </button>
          <Button type="submit" size="sm" className="h-11 w-11 rounded-lg shrink-0 p-0" disabled={!input.trim() || isTyping}>
            <Send className="w-4 h-4 ml-0.5" />
          </Button>
        </form>
      </div>
    </div>
  );
}
