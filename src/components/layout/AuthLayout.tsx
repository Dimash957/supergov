import { Outlet } from 'react-router-dom';

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Abstract Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-cyan/20 blur-3xl rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-gold/10 blur-3xl rounded-full pointer-events-none" />
      
      <div className="w-full max-w-md z-10">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-navy flex items-center justify-center tracking-tight">
            <span className="text-cyan">super</span>gov
          </h1>
          <p className="text-slate-500 mt-3 text-sm font-medium">Государство в твоем смартфоне</p>
        </div>
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl shadow-navy/5 p-8 border border-white/40">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
