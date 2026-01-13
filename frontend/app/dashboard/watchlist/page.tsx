"use client";

import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import {
  Trash2,
  Settings,
  Play,
  Pause,
  ExternalLink,
  Calendar,
  MapPin,
  AlertCircle,
  Zap
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { watchesApi, Watch } from '@/lib/api/watches';

export default function WatchlistPage() {
  const [watches, setWatches] = useState<Watch[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadWatches();
  }, []);

  const loadWatches = async () => {
    try {
      const data = await watchesApi.getAll();
      setWatches(data);
    } catch (error: any) {
      console.error('Failed to load watches:', error);
      toast.error(error.message || 'Failed to load watches');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (watchId: string) => {
    try {
      await watchesApi.delete(watchId);
      setWatches(watches.filter(w => w.id !== watchId));
      toast.success('Watch removed successfully');
    } catch (error: any) {
      console.error('Failed to delete watch:', error);
      toast.error(error.message || 'Failed to delete watch');
    }
  };

  const toggleStatus = async (watchId: string) => {
    const watch = watches.find(w => w.id === watchId);
    if (!watch) return;

    const newStatus = watch.status === 'active' ? 'paused' : 'active';
    
    try {
      const updated = await watchesApi.update(watchId, { status: newStatus });
      setWatches(watches.map(w => w.id === watchId ? updated : w));
      toast.success('Watch status updated');
    } catch (error: any) {
      console.error('Failed to update watch status:', error);
      toast.error(error.message || 'Failed to update watch status');
    }
  };

  const updateFrequency = async (watchId: string, freq: 'daily' | 'hourly' | 'sniper') => {
    try {
      const updated = await watchesApi.update(watchId, { frequency: freq });
      setWatches(watches.map(w => w.id === watchId ? updated : w));
      toast.success(`Frequency set to ${freq}`);
    } catch (error: any) {
      console.error('Failed to update frequency:', error);
      toast.error(error.message || 'Failed to update frequency');
    }
  };

  const formatDates = (checkIn: string, checkOut: string) => {
    const checkInDate = new Date(checkIn);
    const checkOutDate = new Date(checkOut);
    const checkInStr = checkInDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const checkOutStr = checkOutDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return `${checkInStr} - ${checkOutStr}`;
  };

  const formatLastChecked = (lastScannedAt?: string) => {
    if (!lastScannedAt) return 'Never';
    
    const now = new Date();
    const scanned = new Date(lastScannedAt);
    const diffMs = now.getTime() - scanned.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  if (isLoading) return null;

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">Your Watchlist</h1>
          <p className="text-sm sm:text-base text-slate-400">Manage your active property monitors.</p>
        </div>
        <div className="bg-slate-900/50 border border-white/10 rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm text-slate-400 self-start sm:self-auto">
          {watches.length} / 5 Active Watches
        </div>
      </div>

      {watches.length === 0 ? (
        <div className="text-center py-12 sm:py-20 bg-slate-900/30 border border-white/10 rounded-xl sm:rounded-2xl border-dashed">
          <div className="w-12 sm:w-16 h-12 sm:h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
            <AlertCircle className="w-6 sm:w-8 h-6 sm:h-8 text-slate-500" />
          </div>
          <h3 className="text-lg sm:text-xl font-bold text-white mb-2">No active watches</h3>
          <p className="text-sm sm:text-base text-slate-400 mb-4 sm:mb-6 px-4">Start by discovering properties to monitor.</p>
          <a
            href="/dashboard/discover"
            className="inline-flex items-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 rounded-full bg-white text-slate-950 font-bold hover:bg-slate-200 transition-colors touch-manipulation active:scale-[0.98] text-sm sm:text-base"
          >
            Find Properties
          </a>
        </div>
      ) : (
        <div className="grid gap-4 sm:gap-6">
          <AnimatePresence>
            {watches.map((watch) => (
              <motion.div
                key={watch.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                layout
                className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-xl sm:rounded-2xl p-4 sm:p-6 flex flex-col gap-4 sm:gap-6 group hover:border-white/20 transition-all"
              >
                {/* Top section: Image + Basic Info */}
                <div className="flex gap-3 sm:gap-4">
                  {/* Image */}
                  <div className="w-20 sm:w-32 md:w-48 h-20 sm:h-24 md:h-32 rounded-lg sm:rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex-shrink-0 relative overflow-hidden">
                    {watch.imageUrl ? (
                      <img
                        src={watch.imageUrl}
                        alt={watch.propertyName}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center text-white/20">
                        <MapPin className="w-6 sm:w-8 h-6 sm:h-8" />
                      </div>
                    )}
                    <div className={`absolute top-1.5 sm:top-2 left-1.5 sm:left-2 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded text-[10px] sm:text-xs font-bold uppercase tracking-wider ${
                      watch.status === 'active' ? 'bg-green-500 text-white' :
                      watch.status === 'paused' ? 'bg-yellow-500 text-black' : 'bg-red-500 text-white'
                    }`}>
                      {watch.status}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start gap-2 mb-1 sm:mb-2">
                      <h3 className="text-sm sm:text-lg md:text-xl font-bold text-white line-clamp-2 sm:truncate">{watch.propertyName}</h3>
                      <a
                        href={watch.propertyUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-500 hover:text-white transition-colors flex-shrink-0 p-1 touch-manipulation"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink className="w-4 sm:w-5 h-4 sm:h-5" />
                      </a>
                    </div>

                    <div className="flex flex-col sm:flex-row sm:flex-wrap gap-1 sm:gap-3 text-xs sm:text-sm text-slate-400 mb-2 sm:mb-3">
                      <div className="flex items-center gap-1.5 sm:gap-2">
                        <MapPin className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" />
                        <span className="truncate">{watch.location}</span>
                      </div>
                      <div className="flex items-center gap-1.5 sm:gap-2">
                        <Calendar className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" />
                        <span>{formatDates(watch.checkInDate, watch.checkOutDate)}</span>
                      </div>
                    </div>

                    <div className="text-[10px] sm:text-xs text-slate-500">
                      Last checked: {formatLastChecked(watch.lastScannedAt)}
                    </div>
                  </div>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap items-center gap-2 sm:gap-4 pt-3 sm:pt-0 border-t sm:border-t-0 border-white/10">
                  {/* Frequency selector */}
                  <div className="flex items-center gap-1 sm:gap-2 bg-slate-950 rounded-lg p-0.5 sm:p-1 border border-white/10 flex-shrink-0">
                    {(['daily', 'hourly', 'sniper'] as const).map((freq) => (
                      <button
                        key={freq}
                        onClick={() => updateFrequency(watch.id, freq)}
                        className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-md text-[10px] sm:text-xs font-medium transition-all touch-manipulation ${
                          watch.frequency === freq
                            ? 'bg-white/10 text-white shadow-sm'
                            : 'text-slate-500 hover:text-slate-300'
                        }`}
                      >
                        {freq.charAt(0).toUpperCase() + freq.slice(1)}
                      </button>
                    ))}
                  </div>

                  <div className="flex-1" />

                  {/* Action buttons */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleStatus(watch.id)}
                      className={`p-2 sm:p-2.5 rounded-lg border transition-colors touch-manipulation active:scale-[0.95] ${
                        watch.status === 'active'
                          ? 'border-yellow-500/20 text-yellow-500 hover:bg-yellow-500/10'
                          : 'border-green-500/20 text-green-500 hover:bg-green-500/10'
                      }`}
                      title={watch.status === 'active' ? 'Pause Scanning' : 'Resume Scanning'}
                    >
                      {watch.status === 'active' ? <Pause className="w-4 sm:w-5 h-4 sm:h-5" /> : <Play className="w-4 sm:w-5 h-4 sm:h-5" />}
                    </button>

                    <button
                      onClick={() => handleDelete(watch.id)}
                      className="p-2 sm:p-2.5 rounded-lg border border-red-500/20 text-red-500 hover:bg-red-500/10 transition-colors touch-manipulation active:scale-[0.95]"
                      title="Delete Watch"
                    >
                      <Trash2 className="w-4 sm:w-5 h-4 sm:h-5" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}

