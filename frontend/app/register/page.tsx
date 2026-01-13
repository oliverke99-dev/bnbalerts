"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, Mail, Lock, Phone, ArrowRight, CheckCircle } from 'lucide-react';
import AuthLayout from '@/components/auth-layout';
import { auth } from '@/lib/auth';

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState<'details' | 'verify'>('details');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string>('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    phone: '',
    otp: ''
  });

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const user = await auth.register(formData.email, formData.password, formData.phone);
      setUserId(user.id);
      toast.success('Account created! Please verify your phone.');
      setStep('verify');
    } catch (error) {
      toast.error('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const success = await auth.verifyPhone(userId, formData.otp);
      if (success) {
        toast.success('Phone verified successfully!');
        router.push('/dashboard');
      } else {
        toast.error('Invalid code. Try 123456');
      }
    } catch (error) {
      toast.error('Verification failed.');
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'verify') {
    return (
      <AuthLayout 
        title="Verify Phone" 
        subtitle={`We sent a code to ${formData.phone}`}
      >
        <form onSubmit={handleVerify} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Verification Code</label>
            <input
              type="text"
              required
              className="w-full bg-slate-950 border border-white/10 rounded-lg py-3 px-4 text-center text-2xl tracking-widest text-white placeholder:text-slate-700 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              placeholder="000000"
              maxLength={6}
              value={formData.otp}
              onChange={(e) => setFormData({ ...formData, otp: e.target.value })}
            />
            <p className="text-xs text-slate-500 text-center">
              For demo purposes, use code: <span className="text-white font-mono">123456</span>
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 rounded-lg shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Verify & Continue <CheckCircle className="w-5 h-5" />
              </>
            )}
          </button>
        </form>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout 
      title="Create Account" 
      subtitle="Start monitoring properties in seconds"
    >
      <form onSubmit={handleRegister} className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="email"
              required
              className="w-full bg-slate-950 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              placeholder="you@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">Phone Number</label>
          <div className="relative">
            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="tel"
              required
              className="w-full bg-slate-950 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              placeholder="+15551234567"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
          <p className="text-xs text-slate-500">
            Enter phone in E.164 format (e.g., +15551234567)
          </p>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="password"
              required
              className="w-full bg-slate-950 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>
        </div>

        <div className="flex items-start gap-2 pt-2">
          <input 
            type="checkbox" 
            required 
            className="mt-1 rounded border-white/10 bg-slate-950 text-purple-600 focus:ring-purple-500"
          />
          <p className="text-xs text-slate-400">
            I agree to the Terms of Service and consent to receive SMS notifications. Message and data rates may apply.
          </p>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 rounded-lg shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Create Account <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>

        <div className="text-center text-slate-400 text-sm">
          Already have an account?{' '}
          <Link href="/login" className="text-white font-medium hover:underline">
            Sign in
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
