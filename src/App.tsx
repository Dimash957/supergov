import { Suspense, type ComponentProps } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { StackProvider, useUser } from '@stackframe/stack';
import { stack, stackInitError } from './lib/stack';

import { AuthLayout } from './components/layout/AuthLayout';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Login } from './pages/auth/Login';
import { Register } from './pages/auth/Register';

import { Dashboard } from './pages/dashboard/Dashboard';
import { Chat } from './pages/chat/Chat';
import { Services } from './pages/services/Services';
import { ApplicationWizard } from './pages/services/ApplicationWizard';
import { Applications } from './pages/applications/Applications';
import { Tracker } from './pages/tracker/Tracker';
import { Benefits } from './pages/benefits/Benefits';
import { ComplaintsMap } from './pages/map/ComplaintsMap';
import { AgenciesRating } from './pages/rating/AgenciesRating';
import { Profile } from './pages/profile/Profile';
import { EgovPage } from './pages/eGov/EgovPage';
import { DocumentsPage } from './pages/documents/DocumentsPage';
import { UserProfileBootstrap } from './components/UserProfileBootstrap';
import { getOtpToken } from './lib/apiHeaders';

const queryClient = new QueryClient();

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const stackUser = useUser();
  const otp = typeof localStorage !== 'undefined' ? getOtpToken() : null;
  if (!stackUser && !otp) {
    return <Navigate to="/login" replace />;
  }
  return (
    <>
      <UserProfileBootstrap />
      {children}
    </>
  );
}

export default function App() {
  if (stackInitError || !stack) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100 p-6">
        <div className="max-w-lg rounded-2xl border border-amber-200 bg-white p-8 shadow-lg">
          <h1 className="text-xl font-bold text-navy mb-3">Не настроен Stack Auth</h1>
          <p className="text-slate-600 text-sm leading-relaxed mb-4">{stackInitError}</p>
          <p className="text-xs text-slate-500">
            Файл <code className="rounded bg-slate-100 px-1">.env</code> должен лежать в папке{' '}
            <code className="rounded bg-slate-100 px-1">gogo</code> (рядом с{' '}
            <code className="rounded bg-slate-100 px-1">package.json</code>), не только в{' '}
            <code className="rounded bg-slate-100 px-1">backend</code>.
          </p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <StackProvider app={stack as ComponentProps<typeof StackProvider>['app']}>
        <QueryClientProvider client={queryClient}>
        <Suspense fallback={<div className="h-screen w-full flex items-center justify-center bg-slate-50"><div className="w-10 h-10 border-4 border-cyan border-t-transparent rounded-full animate-spin"></div></div>}>
        <Router>
          <Routes>
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>

            {/* Dashboard Routes (Protected) */}
            <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/services" element={<Services />} />
              <Route path="/application/new/:serviceType" element={<ApplicationWizard />} />
              <Route path="/applications" element={<Applications />} />
              <Route path="/tracker" element={<Tracker />} />
              <Route path="/benefits" element={<Benefits />} />
              <Route path="/map" element={<ComplaintsMap />} />
              <Route path="/rating" element={<AgenciesRating />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/egov" element={<EgovPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
            
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
        </Suspense>
        <Toaster position="top-right" />
      </QueryClientProvider>
    </StackProvider>
    </ErrorBoundary>
  );
}
