"use client";

import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { User, Mail, Phone, Shield, Bell, Save, Loader2 } from 'lucide-react';
import { auth } from '@/lib/auth';

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: 'Demo User',
    email: '',
    phone: '',
    notifications: {
      sms: true,
      email: false,
      marketing: false
    }
  });

  useEffect(() => {
    const currentUser = auth.getUser();
    if (currentUser) {
      setUser(currentUser);
      setFormData(prev => ({
        ...prev,
        email: currentUser.email,
        phone: currentUser.phone || ''
      }));
    }
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('Settings saved successfully');
    setIsLoading(false);
  };

  if (!user) return null;

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Account Settings</h1>
        <p className="text-slate-400">Manage your profile and notification preferences.</p>
      </div>

      <form onSubmit={handleSave} className="space-y-8">
        {/* Profile Section */}
        <section className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <User className="w-6 h-6 text-purple-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Profile Information</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Full Name</label>
              <input
                type="text"
                className="w-full bg-slate-950 border border-white/10 rounded-lg py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="email"
                  disabled
                  className="w-full bg-slate-950/50 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-slate-400 cursor-not-allowed"
                  value={formData.email}
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Phone Number</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="tel"
                  className="w-full bg-slate-950 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Notifications Section */}
        <section className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-pink-500/10 rounded-lg">
              <Bell className="w-6 h-6 text-pink-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Notifications</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-950/50 rounded-xl border border-white/5">
              <div>
                <h3 className="font-medium text-white">SMS Alerts</h3>
                <p className="text-sm text-slate-400">Receive instant text messages when properties become available.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer"
                  checked={formData.notifications.sms}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    notifications: { ...formData.notifications, sms: e.target.checked } 
                  })}
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-950/50 rounded-xl border border-white/5">
              <div>
                <h3 className="font-medium text-white">Email Summaries</h3>
                <p className="text-sm text-slate-400">Receive daily summaries of your watch activity.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer"
                  checked={formData.notifications.email}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    notifications: { ...formData.notifications, email: e.target.checked } 
                  })}
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </div>
          </div>
        </section>

        {/* Security Section */}
        <section className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Security</h2>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-white">Password</h3>
              <p className="text-sm text-slate-400">Last changed 3 months ago</p>
            </div>
            <button type="button" className="px-4 py-2 rounded-lg border border-white/10 hover:bg-white/5 transition-colors text-sm font-medium">
              Change Password
            </button>
          </div>
        </section>

        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className="px-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Save className="w-5 h-5" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
