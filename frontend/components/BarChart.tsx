"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Title,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Title);

export function BarChart({
  title,
  labels,
  values,
  suffix = "%",
}: {
  title: string;
  labels: string[];
  values: number[];
  suffix?: string;
}) {
  return (
    <div className="card">
      <p className="text-sm font-medium text-ink mb-3">{title}</p>
      <Bar
        data={{
          labels,
          datasets: [
            {
              data: values,
              backgroundColor: "#4f46e5",
              borderRadius: 6,
              maxBarThickness: 36,
            },
          ],
        }}
        options={{
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.formattedValue}${suffix}`,
              },
            },
          },
          scales: {
            y: { beginAtZero: true, max: suffix === "%" ? 100 : undefined },
          },
        }}
      />
    </div>
  );
}
