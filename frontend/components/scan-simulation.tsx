"use client";

import React, { useEffect } from 'react';
import { toast } from 'sonner';
import { Zap } from 'lucide-react';

// This component simulates the backend scanning engine
// It triggers alerts for new watches after 30 seconds for demo purposes
// And randomly triggers "availability found" alerts for active watches
export default function ScanSimulation() {
  useEffect(() => {
    const checkWatches = () => {
      const watches = JSON.parse(localStorage.getItem('bnb_watches') || '[]');
      if (watches.length === 0) return;

      const now = Date.now();
      let updated = false;

      // 1. Check for Demo Triggers (30 seconds after creation)
      const demoTarget = watches.find((w: any) => 
        !w.demoAlertTriggered && 
        w.status === 'active' &&
        (now - new Date(w.createdAt).getTime() > 30000) // > 30 seconds
      );

      if (demoTarget) {
        triggerAlert(demoTarget);
        
        // Mark as triggered
        const updatedWatches = watches.map((w: any) => 
          w.watchId === demoTarget.watchId ? { ...w, demoAlertTriggered: true } : w
        );
        localStorage.setItem('bnb_watches', JSON.stringify(updatedWatches));
        return; // Prioritize demo alert
      }

      // 2. Random Background Alerts (Low probability)
      // Only if no demo alert was just triggered
      if (Math.random() > 0.95) { // 5% chance every 5 seconds
        const activeWatches = watches.filter((w: any) => w.status === 'active');
        if (activeWatches.length > 0) {
          const randomWatch = activeWatches[Math.floor(Math.random() * activeWatches.length)];
          triggerAlert(randomWatch);
        }
      }
    };

    const triggerAlert = (watch: any) => {
      // Play sound (optional, browser might block)
      // const audio = new Audio('/notification.mp3');
      // audio.play().catch(e => console.log('Audio blocked'));

      toast.custom((t) => (
        <div className="bg-slate-900 border border-green-500/50 rounded-xl p-4 shadow-2xl shadow-green-500/20 flex items-start gap-4 w-full max-w-md animate-in slide-in-from-top-5 duration-300">
          <div className="bg-green-500/20 p-2 rounded-full">
            <Zap className="w-6 h-6 text-green-400 fill-green-400 animate-pulse" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-white text-lg mb-1">Availability Found!</h3>
            <p className="text-slate-300 text-sm mb-3">
              <span className="font-semibold text-white">{watch.name}</span> is now available for your dates.
            </p>
            <div className="flex gap-2">
              <button 
                onClick={() => {
                  toast.dismiss(t);
                  window.open(`https://www.airbnb.com/rooms/${watch.id}`, '_blank');
                }}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors"
              >
                Book Now
              </button>
              <button 
                onClick={() => toast.dismiss(t)}
                className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      ), { duration: 10000 });
    };

    // Check every 5 seconds
    const interval = setInterval(checkWatches, 5000);

    return () => clearInterval(interval);
  }, []);

  return null;
}
