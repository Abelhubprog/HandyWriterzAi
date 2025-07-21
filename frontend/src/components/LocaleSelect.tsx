"use client";

import * as React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function LocaleSelect() {
  return (
    <Select>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Language" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="en-US">English (United States)</SelectItem>
        <SelectItem value="en-GB">English (United Kingdom)</SelectItem>
        <SelectItem value="es-ES">Español (España)</SelectItem>
      </SelectContent>
    </Select>
  );
}
