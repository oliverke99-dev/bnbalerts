"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Bell,
  Search,
  Clock,
  ArrowRight,
  Activity,
  CheckCircle,
  AlertCircle,
  MapPin
} from 'lucide-react';
import { auth } from '@/lib/auth';
import { format, formatDistanceToNow } from 'date-fns';

interface Watch {
  id: string;
  propertyName: string;
  location: string;
  imageUrl?: string;
  checkInDate: string;
  checkOutDate: string;
  status: string;
  lastScannedAt?: string;
  price: string;
}

interface DashboardStats {
  activeWatches: number;
  scansToday: number;
  alertsSent: number;
  recentActivity: Array<{
    type: string;
    timestamp: string;
    status: string;
    result?: string;
    message?: string;
  }>;
}

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [watches, setWatches] = useState<Watch[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentUser = auth.getUser();
    setUser(currentUser);
    
    if (currentUser) {
      fetchDashboardData();
    }
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('bnb_alerts_token') : null;
      if (!token) return;
      
      // Fetch watches
      const watchesRes = await fetch('http://localhost:8000/api/v1/watches', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (watchesRes.ok) {
        const watchesData = await watchesRes.json();
        setWatches(watchesData.slice(0, 3)); // Show only first 3
      }
      
      // Fetch stats
      const statsRes = await fetch('http://localhost:8000/api/v1/stats/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  const statsCards = [
    {
      label: 'Active Watches',
      value: stats?.activeWatches?.toString() || '0',
      icon: Activity,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10'
    },
    {
      label: 'Scans Today',
      value: stats?.scansToday?.toString() || '0',
      icon: Search,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10'
    },
    {
      label: 'Alerts Sent',
      value: stats?.alertsSent?.toString() || '0',
      icon: Bell,
      color: 'text-pink-400',
      bg: 'bg-pink-500/10'
    },
  ];

  const formatActivityMessage = (activity: any) => {
    if (activity.type === 'scan') {
      const result = activity.result === 'available' ? 'Available' :
                     activity.result === 'unavailable' ? 'Unavailable' : 'Checked';
      return `Property scan completed: ${result}`;
    } else if (activity.type === 'notification') {
      return activity.message || 'Notification sent';
    }
    return 'Activity logged';
  };

  const formatActivityTime = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  const getActivityStatus = (activity: any) => {
    if (activity.type === 'scan') {
      return activity.result === 'available' ? 'alert' : 'success';
    }
    return activity.status === 'delivered' ? 'alert' : 'info';
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-0.5 sm:mb-1">Dashboard</h1>
          <p className="text-sm sm:text-base text-slate-400 truncate">Welcome back, {user.email}</p>
        </div>
        <Link
          href="/dashboard/discover"
          className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold shadow-lg shadow-purple-500/25 active:scale-[0.98] transition-all touch-manipulation text-sm sm:text-base w-full sm:w-auto sm:self-start"
        >
          <Search className="w-4 h-4" />
          Find New Property
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-3 sm:gap-6">
        {statsCards.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-xl sm:rounded-2xl p-3 sm:p-6"
          >
            <div className="flex items-center justify-between mb-2 sm:mb-4">
              <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-4 sm:w-6 h-4 sm:h-6 ${stat.color}`} />
              </div>
              <span className="hidden sm:inline text-xs font-medium text-slate-500 bg-white/5 px-2 py-1 rounded-full">
                {loading ? '...' : 'Live'}
              </span>
            </div>
            <h3 className="text-xl sm:text-3xl font-bold text-white mb-0.5 sm:mb-1">
              {loading ? '...' : stat.value}
            </h3>
            <p className="text-slate-400 text-[10px] sm:text-sm truncate">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
        {/* Active Watches Preview */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg sm:text-xl font-bold text-white">Active Watches</h2>
            <Link href="/dashboard/watchlist" className="text-xs sm:text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1 touch-manipulation">
              View All <ArrowRight className="w-3 sm:w-4 h-3 sm:h-4" />
            </Link>
          </div>

          <div className="space-y-3 sm:space-y-4">
            {loading ? (
              <div className="text-center py-6 sm:py-8 text-slate-400 text-sm">Loading watches...</div>
            ) : watches.length === 0 ? (
              <div className="text-center py-6 sm:py-8">
                <p className="text-slate-400 mb-3 sm:mb-4 text-sm">No active watches yet</p>
                <Link
                  href="/dashboard/discover"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 text-white text-sm hover:bg-purple-700 transition-colors touch-manipulation active:scale-[0.98]"
                >
                  <Search className="w-4 h-4" />
                  Find Your First Property
                </Link>
              </div>
            ) : (
              watches.map((watch) => (
                <div key={watch.id} className="group bg-slate-900/50 border border-white/10 rounded-xl p-3 sm:p-4 hover:bg-white/5 transition-colors flex items-start sm:items-center gap-3 sm:gap-4">
                  <div className="w-12 sm:w-16 h-12 sm:h-16 rounded-lg bg-slate-800 flex-shrink-0 overflow-hidden relative">
                    {watch.imageUrl ? (
                      <img
                        src={watch.imageUrl}
                        alt={watch.propertyName}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-600">
                        <MapPin className="w-5 sm:w-6 h-5 sm:h-6" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white text-sm sm:text-base line-clamp-1">{watch.propertyName}</h3>
                    <p className="text-xs sm:text-sm text-slate-400 line-clamp-1">
                      {watch.location} • {format(new Date(watch.checkInDate), 'MMM d')} - {format(new Date(watch.checkOutDate), 'MMM d')}
                    </p>
                    {/* Mobile: Show status inline */}
                    <div className="flex items-center gap-2 mt-1.5 sm:hidden">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                        watch.status === 'active'
                          ? 'bg-green-500/10 text-green-400 border-green-500/20'
                          : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                      }`}>
                        {watch.status === 'active' && (
                          <span className="relative flex h-1.5 w-1.5">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                          </span>
                        )}
                        {watch.status === 'active' ? 'Active' : watch.status}
                      </span>
                      {watch.lastScannedAt && (
                        <span className="text-[10px] text-slate-500">
                          {formatDistanceToNow(new Date(watch.lastScannedAt), { addSuffix: true })}
                        </span>
                      )}
                    </div>
                  </div>
                  {/* Desktop: Show status on right */}
                  <div className="hidden sm:flex flex-col items-end gap-2 flex-shrink-0">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                      watch.status === 'active'
                        ? 'bg-green-500/10 text-green-400 border-green-500/20'
                        : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                    }`}>
                      {watch.status === 'active' && (
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                      )}
                      {watch.status === 'active' ? 'Active' : watch.status}
                    </span>
                    {watch.lastScannedAt && (
                      <span className="text-xs text-slate-500">
                        Last: {formatDistanceToNow(new Date(watch.lastScannedAt), { addSuffix: true })}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Activity Feed */}
        <div className="space-y-4 sm:space-y-6">
          <h2 className="text-lg sm:text-xl font-bold text-white">Recent Activity</h2>
          <div className="bg-slate-900/50 border border-white/10 rounded-xl sm:rounded-2xl p-4 sm:p-6">
            {loading ? (
              <div className="text-center py-4 text-slate-400 text-sm">Loading activity...</div>
            ) : !stats?.recentActivity || stats.recentActivity.length === 0 ? (
              <div className="text-center py-6 sm:py-8 text-slate-400">
                <Activity className="w-6 sm:w-8 h-6 sm:h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No recent activity</p>
              </div>
            ) : (
              <div className="space-y-4 sm:space-y-6">
                {stats.recentActivity.map((activity, index) => {
                  const activityStatus = getActivityStatus(activity);
                  return (
                    <div key={index} className="flex gap-3 sm:gap-4 relative">
                      <div className="flex flex-col items-center">
                        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                          activityStatus === 'alert' ? 'bg-pink-500' :
                          activityStatus === 'success' ? 'bg-green-500' : 'bg-slate-500'
                        }`} />
                        {index < stats.recentActivity.length - 1 && (
                          <div className="w-px h-full bg-white/10 my-2 absolute top-2 bottom-[-16px] sm:bottom-[-24px]" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs sm:text-sm text-white font-medium line-clamp-2">
                          {formatActivityMessage(activity)}
                        </p>
                        <p className="text-[10px] sm:text-xs text-slate-500 mt-0.5 sm:mt-1">
                          {formatActivityTime(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
