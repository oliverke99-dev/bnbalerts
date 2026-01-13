"use client";

import * as React from "react";
import { DateRange } from "react-day-picker";
import { format } from "date-fns";

import { cn } from "@/lib/utils";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface DateRangePickerProps {
  date?: DateRange;
  onDateChange?: (date: DateRange | undefined) => void;
  className?: string;
}

export function DateRangePicker({
  date,
  onDateChange,
  className,
}: DateRangePickerProps) {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <div className="flex rounded-xl border border-white/10 bg-slate-950 overflow-hidden cursor-pointer hover:border-white/20 transition-colors">
            {/* Check-in */}
            <div className="flex-1 px-4 py-3 border-r border-white/10">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">
                Check-in
              </div>
              <div className={cn(
                "text-sm",
                date?.from ? "text-white" : "text-slate-500"
              )}>
                {date?.from ? format(date.from, "MMM d, yyyy") : "Add date"}
              </div>
            </div>
            
            {/* Check-out */}
            <div className="flex-1 px-4 py-3">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">
                Check-out
              </div>
              <div className={cn(
                "text-sm",
                date?.to ? "text-white" : "text-slate-500"
              )}>
                {date?.to ? format(date.to, "MMM d, yyyy") : "Add date"}
              </div>
            </div>
          </div>
        </PopoverTrigger>
        <PopoverContent 
          className="w-auto p-0 bg-slate-900 border-white/10 rounded-2xl shadow-2xl" 
          align="center"
          sideOffset={8}
        >
          <div className="p-4">
            {/* Header */}
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold text-white">
                {!date?.from 
                  ? "Select check-in date" 
                  : !date?.to 
                    ? "Select check-out date"
                    : `${Math.ceil((date.to.getTime() - date.from.getTime()) / (1000 * 60 * 60 * 24))} nights`
                }
              </h3>
              {date?.from && date?.to && (
                <p className="text-sm text-slate-400 mt-1">
                  {format(date.from, "MMM d")} – {format(date.to, "MMM d, yyyy")}
                </p>
              )}
            </div>
            
            <Calendar
              mode="range"
              defaultMonth={date?.from}
              selected={date}
              onSelect={(newDate) => {
                onDateChange?.(newDate);
                // Close popover when both dates are selected
                if (newDate?.from && newDate?.to) {
                  setTimeout(() => setIsOpen(false), 300);
                }
              }}
              numberOfMonths={2}
              disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
              className="text-white"
            />
            
            {/* Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-white/10 mt-4">
              <button
                onClick={() => {
                  onDateChange?.(undefined);
                }}
                className="text-sm font-semibold text-white underline underline-offset-2 hover:text-slate-300 transition-colors"
              >
                Clear dates
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="px-6 py-2.5 bg-white text-slate-900 rounded-lg font-semibold text-sm hover:bg-slate-100 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}