import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
          <div className="bg-white p-8 rounded-2xl shadow-xl max-w-lg w-full border border-red-100">
            <h1 className="text-2xl font-bold text-red-600 mb-2">Ошибка Инициализации</h1>
            <p className="text-slate-600 text-sm mb-4">
              Приложение не смогло запуститься. Скорее всего, это связано с отсутствием или недействительностью ключей авторизации Stack Auth.
            </p>
            <p className="text-slate-600 text-sm mb-6">
              Пожалуйста, добавьте <strong>VITE_STACK_PUBLISHABLE_KEY</strong> в ваш файл <code>.env</code> в корне проекта.
            </p>
            <div className="bg-red-50 p-4 rounded-xl text-xs font-mono text-red-800 break-words border border-red-100">
              {this.state.error?.message || "Unknown error occurred"}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
