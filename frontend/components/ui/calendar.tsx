"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { DayPicker } from "react-day-picker";

import { cn } from "@/lib/utils";

function Calendar({
  className,
  classNames,
  showOutsideDays = false,
  ...props
}: React.ComponentProps<typeof DayPicker>) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-4", className)}
      classNames={{
        months: "flex flex-col sm:flex-row gap-8",
        month: "flex flex-col gap-4",
        month_caption: "flex justify-center pt-1 relative items-center w-full",
        caption_label: "text-base font-semibold text-white",
        nav: "flex items-center gap-1",
        button_previous: cn(
          "absolute left-0 h-9 w-9 bg-transparent p-0 hover:bg-white/10 rounded-full flex items-center justify-center transition-colors",
        ),
        button_next: cn(
          "absolute right-0 h-9 w-9 bg-transparent p-0 hover:bg-white/10 rounded-full flex items-center justify-center transition-colors",
        ),
        month_grid: "w-full border-collapse",
        weekdays: "flex mb-2",
        weekday:
          "text-slate-500 rounded-md w-10 font-medium text-xs uppercase text-center",
        week: "flex w-full",
        day: cn(
          "relative p-0 text-center text-sm focus-within:relative focus-within:z-20 h-10 w-10",
        ),
        day_button: cn(
          "h-10 w-10 p-0 font-normal rounded-full flex items-center justify-center transition-all",
          "hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/20",
        ),
        range_start:
          "rounded-l-full bg-white/10 [&>.rdp-day_button]:bg-white [&>.rdp-day_button]:text-slate-900 [&>.rdp-day_button]:hover:bg-white [&>.rdp-day_button]:font-semibold",
        range_end:
          "rounded-r-full bg-white/10 [&>.rdp-day_button]:bg-white [&>.rdp-day_button]:text-slate-900 [&>.rdp-day_button]:hover:bg-white [&>.rdp-day_button]:font-semibold",
        selected:
          "[&>.rdp-day_button]:bg-white [&>.rdp-day_button]:text-slate-900 [&>.rdp-day_button]:hover:bg-white [&>.rdp-day_button]:font-semibold",
        today: "[&>.rdp-day_button]:text-purple-400 [&>.rdp-day_button]:font-semibold",
        outside:
          "text-slate-700 opacity-50 pointer-events-none",
        disabled: "text-slate-700 opacity-50 cursor-not-allowed",
        range_middle:
          "bg-white/10 rounded-none [&>.rdp-day_button]:text-white",
        hidden: "invisible",
        ...classNames,
      }}
      components={{
        Chevron: ({ orientation }) => {
          if (orientation === "left") {
            return <ChevronLeft className="h-5 w-5 text-white" />;
          }
          return <ChevronRight className="h-5 w-5 text-white" />;
        },
      }}
      {...props}
    />
  );
}

export { Calendar };
