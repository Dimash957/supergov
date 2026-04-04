import { create } from 'zustand';

export interface UserProfile {
  iin: string;
  name: string;
  email: string;
  phone: string;
  stackUserId: string;
}

interface AppState {
  user: UserProfile | null;
  language: 'kz' | 'ru' | 'en';
  sidebarOpen: boolean;
  setUser: (user: UserProfile | null) => void;
  setLanguage: (lang: 'kz' | 'ru' | 'en') => void;
  toggleSidebar: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  language: (localStorage.getItem('lang') as 'kz' | 'ru' | 'en') || 'ru',
  sidebarOpen: false,
  setUser: (user) => set({ user }),
  setLanguage: (language) => {
    localStorage.setItem('lang', language);
    set({ language });
  },
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
