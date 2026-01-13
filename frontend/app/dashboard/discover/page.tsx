"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Search, Loader2, Plus, Calendar, MapPin, Users, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { DateRange } from 'react-day-picker';
import { format } from 'date-fns';
import { propertiesApi, PropertyResult } from '@/lib/api/properties';
import { DateRangePicker } from '@/components/date-range-picker';

// Helper to parse Airbnb URL
const parseAirbnbUrl = (url: string) => {
  try {
    const urlObj = new URL(url);
    const params = new URLSearchParams(urlObj.search);
    
    // Extract Location
    let location = 'Unknown Location';
    const pathParts = urlObj.pathname.split('/');
    const sIndex = pathParts.indexOf('s');
    if (sIndex !== -1 && pathParts[sIndex + 1]) {
      // Handle format: /s/Austin--TX/homes
      location = pathParts[sIndex + 1]
        .replace(/--/g, ', ')
        .replace(/-/g, ' ');
      // Capitalize words
      location = location.replace(/\b\w/g, l => l.toUpperCase());
    } else if (params.get('query')) {
      location = params.get('query') || 'Unknown Location';
    }

    // Extract Dates
    const checkin = params.get('checkin');
    const checkout = params.get('checkout');
    let dates = 'Dates not specified';
    if (checkin && checkout) {
      const start = new Date(checkin);
      const end = new Date(checkout);
      // Add one day to fix timezone offset issues often seen with simple Date parsing
      const startFormatted = new Date(start.getTime() + start.getTimezoneOffset() * 60000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      const endFormatted = new Date(end.getTime() + end.getTimezoneOffset() * 60000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      dates = `${startFormatted} - ${endFormatted}`;
    }

    // Extract Guests
    const adults = parseInt(params.get('adults') || '0');
    const children = parseInt(params.get('children') || '0');
    const guests = (adults + children) || 2; // Default to 2 if not found

    return { location, dates, guests };
  } catch (e) {
    console.error("Error parsing URL", e);
    return { location: 'Destination', dates: 'Selected Dates', guests: 2 };
  }
};

// Generator for mock properties
const generateMockProperties = (criteria: { location: string, dates: string, guests: number }) => {
  const titles = [
    `Luxury Villa in ${criteria.location}`,
    `Cozy ${criteria.location} Cottage`,
    `Modern Loft near Center`,
    `Spacious Family Home in ${criteria.location}`,
    `Downtown ${criteria.location} Apartment`,
    `Secluded Retreat`,
    `Historic ${criteria.location} Bungalow`,
    `Penthouse with Views`
  ];

  const images = [
    'bg-gradient-to-br from-blue-500/20 to-purple-500/20',
    'bg-gradient-to-br from-green-500/20 to-emerald-500/20',
    'bg-gradient-to-br from-orange-500/20 to-red-500/20',
    'bg-gradient-to-br from-slate-500/20 to-gray-500/20',
    'bg-gradient-to-br from-pink-500/20 to-rose-500/20',
    'bg-gradient-to-br from-indigo-500/20 to-violet-500/20',
  ];

  // Generate 4-8 properties
  const count = Math.floor(Math.random() * 5) + 4;
  
  return Array.from({ length: count }).map((_, i) => ({
    id: Math.random().toString(36).substring(7),
    name: titles[i % titles.length],
    location: criteria.location,
    dates: criteria.dates,
    guests: criteria.guests,
    price: `$${Math.floor(Math.random() * 500) + 100}/night`,
    image: images[i % images.length],
    status: 'unavailable'
  }));
};

export default function DiscoverPage() {
  const router = useRouter();
  const [searchUrl, setSearchUrl] = useState('');
  const [dateRange, setDateRange] = useState<DateRange | undefined>();
  const [guests, setGuests] = useState(2);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<PropertyResult[] | null>(null);
  const [selectedProperties, setSelectedProperties] = useState<string[]>([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchUrl.includes('airbnb.com')) {
      toast.error('Please enter a valid Airbnb URL');
      return;
    }

    // Check if it's a property URL and dates are required
    const isPropertyUrl = searchUrl.includes('/rooms/');
    if (isPropertyUrl && (!dateRange?.from || !dateRange?.to)) {
      toast.error('Please select check-in and check-out dates for property URLs');
      return;
    }

    setIsSearching(true);
    
    try {
      // Call the real API with dates
      const response = await propertiesApi.discover({
        searchUrl,
        checkIn: dateRange?.from ? format(dateRange.from, 'yyyy-MM-dd') : undefined,
        checkOut: dateRange?.to ? format(dateRange.to, 'yyyy-MM-dd') : undefined,
        guests
      });
      
      setResults(response.properties);
      
      // Parse URL for location display
      const criteria = parseAirbnbUrl(searchUrl);
      toast.success(`Found ${response.count} unavailable properties in ${criteria.location}`);
    } catch (error) {
      console.error('Discovery error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to discover properties. Please try again.');
      setResults(null);
    } finally {
      setIsSearching(false);
    }
  };

  const toggleSelection = (id: string) => {
    if (selectedProperties.includes(id)) {
      setSelectedProperties(prev => prev.filter(p => p !== id));
    } else {
      if (selectedProperties.length >= 5) {
        toast.error('You can only watch up to 5 properties at once');
        return;
      }
      setSelectedProperties(prev => [...prev, id]);
    }
  };

  const handleAddToWatchlist = async () => {
    if (selectedProperties.length === 0 || !results) return;
    
    try {
      // Import the watches API
      const { watchesApi } = await import('@/lib/api/watches');
      
      // Create watches for each selected property
      const createPromises = selectedProperties.map(async (id) => {
        const prop = results.find(p => p.id === id);
        if (!prop) return null;
        
        // Create watch data
        const watchData = {
          propertyId: prop.id,
          propertyName: prop.name,
          propertyUrl: prop.url,
          location: prop.location,
          imageUrl: prop.imageUrl,
          checkInDate: dateRange?.from ? format(dateRange.from, 'yyyy-MM-dd') : '',
          checkOutDate: dateRange?.to ? format(dateRange.to, 'yyyy-MM-dd') : '',
          guests: guests,
          price: prop.price,
          frequency: 'daily' as const, // Default frequency
          partialMatch: false
        };
        
        return await watchesApi.create(watchData);
      });

      await Promise.all(createPromises);
      
      toast.success(`Added ${selectedProperties.length} ${selectedProperties.length === 1 ? 'property' : 'properties'} to your watchlist`);
      router.push('/dashboard/watchlist');
    } catch (error) {
      console.error('Failed to add to watchlist:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to add to watchlist');
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">Discover Properties</h1>
        <p className="text-sm sm:text-base text-slate-400">Paste your Airbnb search URL to find unavailable properties to monitor.</p>
      </div>

      {/* Search Form */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-xl sm:rounded-2xl p-4 sm:p-8 shadow-xl">
        <form onSubmit={handleSearch} className="space-y-3 sm:space-y-4">
          {/* URL Input */}
          <div className="relative">
            <Search className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 w-4 sm:w-5 h-4 sm:h-5 text-slate-500" />
            <input
              type="url"
              required
              placeholder="Paste Airbnb URL here..."
              className="w-full bg-slate-950 border border-white/10 rounded-xl py-3 sm:py-4 pl-10 sm:pl-12 pr-3 sm:pr-4 text-sm sm:text-base text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              value={searchUrl}
              onChange={(e) => setSearchUrl(e.target.value)}
            />
          </div>

          {/* Date and Guest Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <DateRangePicker
              date={dateRange}
              onDateChange={setDateRange}
            />
            <div className="relative">
              <Users className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 w-4 sm:w-5 h-4 sm:h-5 text-slate-500" />
              <input
                type="number"
                placeholder="Guests"
                min="1"
                max="16"
                className="w-full bg-slate-950 border border-white/10 rounded-xl py-3 sm:py-4 pl-10 sm:pl-12 pr-3 sm:pr-4 text-sm sm:text-base text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
                value={guests}
                onChange={(e) => setGuests(parseInt(e.target.value) || 2)}
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSearching}
            className="w-full px-6 sm:px-8 py-3 sm:py-4 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 touch-manipulation text-sm sm:text-base"
          >
            {isSearching ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Find Properties <ArrowRight className="w-4 sm:w-5 h-4 sm:h-5" />
              </>
            )}
          </button>
        </form>
        <div className="mt-3 sm:mt-4 flex flex-wrap items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-slate-500">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0" />
          <span>Dates optional for search URLs</span>
          <span className="hidden sm:inline mx-2">•</span>
          <span className="hidden sm:inline">Supports Airbnb</span>
        </div>
      </div>

      {/* Results Grid */}
      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4 sm:space-y-6"
        >
          <div className="flex flex-col gap-4">
            {results.length === 1 ? (
              <div className="space-y-2">
                <h2 className="text-lg sm:text-xl font-bold text-white">Property Details</h2>
                <p className="text-sm sm:text-base text-slate-400">
                  {results[0].status === 'available'
                    ? 'This property is currently available for your dates!'
                    : 'This property is currently booked. Would you like to monitor it for cancellations?'}
                </p>
              </div>
            ) : (
              <div>
                <h2 className="text-lg sm:text-xl font-bold text-white">Found {results.length} properties</h2>
                <p className="text-sm text-slate-400 mt-1">Currently booked. Select the ones you want to monitor for cancellations.</p>
              </div>
            )}
            {selectedProperties.length > 0 && (
              <button
                onClick={handleAddToWatchlist}
                className="w-full sm:w-auto px-6 py-3 rounded-full bg-white text-slate-950 font-bold hover:bg-slate-200 transition-colors flex items-center justify-center gap-2 touch-manipulation active:scale-[0.98]"
              >
                {results.length === 1 ? 'Monitor This Property' : `Monitor Selected (${selectedProperties.length})`}
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            {results.map((property) => (
              <div
                key={property.id}
                onClick={() => toggleSelection(property.id)}
                className={`group relative bg-slate-900/50 border rounded-xl sm:rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 touch-manipulation active:scale-[0.99] ${
                  selectedProperties.includes(property.id)
                    ? 'border-purple-500 ring-1 ring-purple-500/50'
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                {/* Mobile: Stack layout, Desktop: Side by side */}
                <div className="flex flex-col sm:flex-row sm:h-full">
                  {/* Image */}
                  <div className="w-full sm:w-1/3 h-40 sm:h-auto relative bg-slate-800 flex-shrink-0">
                    {property.imageUrl ? (
                      <img
                        src={property.imageUrl}
                        alt={property.name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center text-white/20 bg-gradient-to-br from-slate-700 to-slate-800">
                        <Search className="w-8 h-8" />
                      </div>
                    )}
                    <div className={`absolute top-2 left-2 px-2 py-1 backdrop-blur-md rounded text-xs font-medium ${
                      property.status === 'available'
                        ? 'bg-green-500/80 text-white'
                        : 'bg-black/50 text-white'
                    }`}>
                      {property.status === 'available' ? 'Available' : 'Booked'}
                    </div>
                    {/* Mobile selection indicator */}
                    <div className={`absolute top-2 right-2 w-6 h-6 rounded-full border flex items-center justify-center transition-colors sm:hidden ${
                      selectedProperties.includes(property.id)
                        ? 'bg-purple-500 border-purple-500'
                        : 'border-white/40 bg-black/30'
                    }`}>
                      {selectedProperties.includes(property.id) && <Plus className="w-4 h-4 text-white" />}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 p-4 sm:p-6 min-w-0">
                    <div className="flex justify-between items-start mb-2 gap-2">
                      <h3 className="font-bold text-white group-hover:text-purple-400 transition-colors line-clamp-2 sm:line-clamp-1 text-sm sm:text-base">
                        {property.name}
                      </h3>
                      {/* Desktop selection indicator */}
                      <div className={`hidden sm:flex w-6 h-6 rounded-full border items-center justify-center transition-colors flex-shrink-0 ${
                        selectedProperties.includes(property.id)
                          ? 'bg-purple-500 border-purple-500'
                          : 'border-white/20 group-hover:border-white/40'
                      }`}>
                        {selectedProperties.includes(property.id) && <Plus className="w-4 h-4 text-white" />}
                      </div>
                    </div>

                    <div className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm text-slate-400 mb-3 sm:mb-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                        <span className="truncate">{property.location}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                        <span>{property.dates}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                        <span>{property.guests} guests</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-3 sm:pt-4 border-t border-white/5">
                      <span className="font-bold text-white text-base sm:text-lg">{property.price}</span>
                      <div className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all duration-300 ${
                        selectedProperties.includes(property.id)
                          ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/25'
                          : 'bg-white/10 text-white group-hover:bg-white/20'
                      }`}>
                        {selectedProperties.includes(property.id) ? 'Selected' : 'Select'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}



