"use client";

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Bell, Search, Clock, Shield, Zap, CheckCircle, ArrowRight } from 'lucide-react';
import Navbar from './navbar';
import Footer from './footer';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-purple-500/30 overflow-x-hidden">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative min-h-[100svh] flex items-center justify-center pt-16 sm:pt-20 overflow-hidden">
        {/* Background Effects - reduced on mobile for performance */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[60%] sm:w-[50%] h-[40%] sm:h-[50%] bg-purple-600/20 rounded-full blur-[80px] sm:blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[60%] sm:w-[50%] h-[40%] sm:h-[50%] bg-pink-600/20 rounded-full blur-[80px] sm:blur-[120px]" />
          <div className="hidden sm:block absolute top-[40%] left-[50%] transform -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-600/10 rounded-full blur-[150px]" />
        </div>

        <div className="container mx-auto px-4 sm:px-6 relative z-10">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-6 sm:mb-8"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs sm:text-sm font-medium text-slate-300">Live Monitoring Active</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-4xl sm:text-5xl md:text-7xl font-bold tracking-tight mb-4 sm:mb-6 leading-[1.1]"
            >
              Secure Your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-orange-400">
                Dream Property
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-base sm:text-lg md:text-xl text-slate-400 mb-8 sm:mb-10 max-w-2xl leading-relaxed px-2"
            >
              Don't settle for leftovers. We monitor booked properties 24/7 and instantly alert you when a cancellation occurs.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 w-full sm:w-auto px-4 sm:px-0"
            >
              <Link
                href="/register"
                className="w-full sm:w-auto px-6 sm:px-8 py-3.5 sm:py-4 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold shadow-lg shadow-purple-500/25 active:scale-[0.98] transition-all duration-300 flex items-center justify-center gap-2 touch-manipulation text-sm sm:text-base"
              >
                Start Monitoring <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="#how-it-works"
                className="w-full sm:w-auto px-6 sm:px-8 py-3.5 sm:py-4 rounded-full bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 backdrop-blur-sm transition-all duration-300 text-center touch-manipulation text-sm sm:text-base"
              >
                How it Works
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-16 sm:py-24 relative">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="text-center mb-10 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-5xl font-bold mb-3 sm:mb-4">Why BnBAlerts?</h2>
            <p className="text-slate-400 text-sm sm:text-lg">Engineered for speed, reliability, and success.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-8">
            {[
              {
                icon: <Clock className="w-5 sm:w-6 h-5 sm:h-6 text-white" />,
                title: "Instant SMS Alerts",
                desc: "Get notified within 60 seconds of a cancellation. Speed is everything when booking high-demand stays.",
                gradient: "from-blue-500 to-cyan-500"
              },
              {
                icon: <Shield className="w-5 sm:w-6 h-5 sm:h-6 text-white" />,
                title: "Anti-Bot Technology",
                desc: "Our distributed scanning engine rotates proxies to ensure we never get blocked by property platforms.",
                gradient: "from-purple-500 to-pink-500"
              },
              {
                icon: <Search className="w-5 sm:w-6 h-5 sm:h-6 text-white" />,
                title: "Smart Discovery",
                desc: "Paste a search URL and we'll find the unavailable properties that match your criteria automatically.",
                gradient: "from-orange-500 to-red-500"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="group relative p-5 sm:p-8 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-300"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-xl sm:rounded-2xl transition-opacity duration-500`} />
                <div className={`w-10 sm:w-12 h-10 sm:h-12 rounded-full bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 sm:mb-6 shadow-lg`}>
                  {feature.icon}
                </div>
                <h3 className="text-lg sm:text-xl font-bold mb-2 sm:mb-3">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed text-sm sm:text-base">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-16 sm:py-24 bg-slate-900/50 relative overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-10 sm:gap-16">
            <div className="flex-1 w-full">
              <h2 className="text-2xl sm:text-3xl md:text-5xl font-bold mb-4 sm:mb-6">
                From "Sold Out" to <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                  "Booked" in 3 Steps
                </span>
              </h2>
              <p className="text-slate-400 text-sm sm:text-lg mb-6 sm:mb-8">
                Stop refreshing the page every hour. Let our robots do the heavy lifting while you sleep.
              </p>
              
              <div className="space-y-5 sm:space-y-8">
                {[
                  { step: "01", title: "Paste Search URL", desc: "Copy the URL from your Airbnb search results, even if everything is booked." },
                  { step: "02", title: "Select Properties", desc: "Choose the specific properties you want to monitor from our discovery list." },
                  { step: "03", title: "Get Notified", desc: "Receive an instant SMS with a direct booking link when dates open up." }
                ].map((item, i) => (
                  <div key={i} className="flex gap-4 sm:gap-6">
                    <div className="text-xl sm:text-2xl font-bold text-slate-700 font-mono flex-shrink-0">{item.step}</div>
                    <div>
                      <h4 className="text-base sm:text-xl font-bold mb-1 sm:mb-2">{item.title}</h4>
                      <p className="text-slate-400 text-sm sm:text-base">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex-1 relative w-full">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 blur-[60px] sm:blur-[100px] opacity-20" />
              <div className="relative bg-slate-950 border border-white/10 rounded-xl sm:rounded-2xl p-4 sm:p-6 shadow-2xl">
                {/* Mock UI Card */}
                <div className="flex items-center justify-between mb-4 sm:mb-6 border-b border-white/10 pb-3 sm:pb-4">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <div className="w-2.5 sm:w-3 h-2.5 sm:h-3 rounded-full bg-red-500" />
                    <div className="w-2.5 sm:w-3 h-2.5 sm:h-3 rounded-full bg-yellow-500" />
                    <div className="w-2.5 sm:w-3 h-2.5 sm:h-3 rounded-full bg-green-500" />
                  </div>
                  <div className="text-[10px] sm:text-xs text-slate-500 font-mono">bnb-alerts-engine</div>
                </div>
                
                <div className="space-y-3 sm:space-y-4 font-mono text-xs sm:text-sm">
                  <div className="flex items-center gap-2 text-green-400">
                    <CheckCircle className="w-3.5 sm:w-4 h-3.5 sm:h-4 flex-shrink-0" />
                    <span>Scanning 5 properties...</span>
                  </div>
                  <div className="pl-5 sm:pl-6 text-slate-500 text-[11px] sm:text-sm">
                    [14:02:31] Property #84920... <span className="text-red-400">Booked</span>
                  </div>
                  <div className="pl-5 sm:pl-6 text-slate-500 text-[11px] sm:text-sm">
                    [14:02:32] Property #19384... <span className="text-red-400">Booked</span>
                  </div>
                  <div className="pl-5 sm:pl-6 text-slate-300 text-[11px] sm:text-sm">
                    [14:02:33] Property #99281... <span className="text-green-400 font-bold">AVAILABLE!</span>
                  </div>
                  <div className="p-2.5 sm:p-3 bg-green-500/10 border border-green-500/20 rounded text-green-300 mt-2 animate-pulse text-[11px] sm:text-sm">
                    <Zap className="w-3.5 sm:w-4 h-3.5 sm:h-4 inline mr-1.5 sm:mr-2" />
                    SMS Sent to +1 (555) ***-****
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950 to-purple-900/20" />
        <div className="container mx-auto px-4 sm:px-6 relative z-10 text-center">
          <h2 className="text-3xl sm:text-4xl md:text-6xl font-bold mb-6 sm:mb-8">Ready to secure your stay?</h2>
          <p className="text-base sm:text-xl text-slate-400 mb-8 sm:mb-10 max-w-2xl mx-auto px-2">
            Join thousands of travelers who stopped searching and started booking.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 px-8 sm:px-10 py-4 sm:py-5 rounded-full bg-white text-slate-950 font-bold text-sm sm:text-lg hover:bg-slate-200 transition-colors shadow-xl shadow-white/10 touch-manipulation active:scale-[0.98]"
          >
            Get Started for Free <ArrowRight className="w-4 sm:w-5 h-4 sm:h-5" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingPage;

