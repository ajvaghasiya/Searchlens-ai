"use client";

import { useEffect, useRef } from "react";

interface Cell {
  x_bucket: number;
  y_bucket: number;
  count: number;
}

const GRID_SIZE = 20;

export function Heatmap({ cells }: { cells: Cell[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const cellW = width / GRID_SIZE;
    const cellH = height / GRID_SIZE;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#f8fafc";
    ctx.fillRect(0, 0, width, height);

    const maxCount = Math.max(1, ...cells.map((c) => c.count));

    cells.forEach((cell) => {
      const intensity = cell.count / maxCount;
      const alpha = 0.15 + intensity * 0.75;
      ctx.fillStyle = `rgba(220, 38, 38, ${alpha})`;
      ctx.fillRect(cell.x_bucket * cellW, cell.y_bucket * cellH, cellW, cellH);
    });

    ctx.strokeStyle = "#e2e8f0";
    for (let i = 0; i <= GRID_SIZE; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cellW, 0);
      ctx.lineTo(i * cellW, height);
      ctx.stroke();
    }
  }, [cells]);

  return (
    <div className="card">
      <p className="text-sm font-medium text-ink mb-3">Click density</p>
      {cells.length === 0 ? (
        <p className="text-sm text-slate-500">No click data yet for this page.</p>
      ) : (
        <canvas ref={canvasRef} width={480} height={320} className="w-full rounded-lg border border-slate-200" />
      )}
    </div>
  );
}
