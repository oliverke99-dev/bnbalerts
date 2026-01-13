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
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Your Watchlist</h1>
          <p className="text-slate-400">Manage your active property monitors.</p>
        </div>
        <div className="bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2 text-sm text-slate-400">
          {watches.length} / 5 Active Watches
        </div>
      </div>

      {watches.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/30 border border-white/10 rounded-2xl border-dashed">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-slate-500" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No active watches</h3>
          <p className="text-slate-400 mb-6">Start by discovering properties to monitor.</p>
          <a 
            href="/dashboard/discover"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-slate-950 font-bold hover:bg-slate-200 transition-colors"
          >
            Find Properties
          </a>
        </div>
      ) : (
        <div className="grid gap-6">
          <AnimatePresence>
            {watches.map((watch) => (
              <motion.div
                key={watch.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                layout
                className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex flex-col md:flex-row gap-6 group hover:border-white/20 transition-all"
              >
                {/* Image */}
                <div className="w-full md:w-48 h-32 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex-shrink-0 relative overflow-hidden">
                  {watch.imageUrl ? (
                    <img
                      src={watch.imageUrl}
                      alt={watch.propertyName}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-white/20">
                      <MapPin className="w-8 h-8" />
                    </div>
                  )}
                  <div className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-bold uppercase tracking-wider ${
                    watch.status === 'active' ? 'bg-green-500 text-white' :
                    watch.status === 'paused' ? 'bg-yellow-500 text-black' : 'bg-red-500 text-white'
                  }`}>
                    {watch.status}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-white truncate pr-4">{watch.propertyName}</h3>
                    <a
                      href={watch.propertyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-slate-500 hover:text-white transition-colors"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-slate-400 mb-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      {watch.location}
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {formatDates(watch.checkInDate, watch.checkOutDate)}
                    </div>
                  </div>

                  <div className="text-xs text-slate-500 mb-6">
                    Last checked: {formatLastChecked(watch.lastScannedAt)}
                  </div>

                  {/* Controls */}
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2 bg-slate-950 rounded-lg p-1 border border-white/10">
                      {(['daily', 'hourly', 'sniper'] as const).map((freq) => (
                        <button
                          key={freq}
                          onClick={() => updateFrequency(watch.id, freq)}
                          className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
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

                    <button
                      onClick={() => toggleStatus(watch.id)}
                      className={`p-2 rounded-lg border transition-colors ${
                        watch.status === 'active'
                          ? 'border-yellow-500/20 text-yellow-500 hover:bg-yellow-500/10'
                          : 'border-green-500/20 text-green-500 hover:bg-green-500/10'
                      }`}
                      title={watch.status === 'active' ? 'Pause Scanning' : 'Resume Scanning'}
                    >
                      {watch.status === 'active' ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                    </button>

                    <button
                      onClick={() => handleDelete(watch.id)}
                      className="p-2 rounded-lg border border-red-500/20 text-red-500 hover:bg-red-500/10 transition-colors"
                      title="Delete Watch"
                    >
                      <Trash2 className="w-5 h-5" />
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

