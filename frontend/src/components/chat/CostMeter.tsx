"use client";

import { useState, useEffect } from "react";

async function fetchCostEstimate(prompt: string): Promise<{ cost: number }> {
  // In a real application, this would make an API call to the backend.
  // For now, we'll just estimate the cost based on the prompt length.
  const cost = (prompt.length / 1000) * 0.01; // $0.01 per 1000 characters
  return { cost };
}

export function CostMeter({ prompt }: { prompt: string }) {
  const [cost, setCost] = useState<number | null>(null);

  useEffect(() => {
    if (prompt) {
      fetchCostEstimate(prompt).then(({ cost }) => setCost(cost));
    } else {
      setCost(null);
    }
  }, [prompt]);

  if (cost === null) {
    return null;
  }

  return (
    <div className="text-sm text-muted-foreground">
      Estimated cost: ${cost.toFixed(4)}
    </div>
  );
}
