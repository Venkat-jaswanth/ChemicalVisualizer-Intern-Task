// frontend-web/client/src/components/DataVisualization.js

import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from "chart.js";

// We need to register the components we're using
ChartJS.register(ArcElement, Tooltip, Legend, Title);

const DataVisualization = ({ summary }) => {
  if (!summary) {
    return <p>Upload a dataset to see the analysis.</p>;
  }

  // --- 1. Prepare Data for Averages Table ---
  // We use .toFixed(2) to round to 2 decimal places
  const averages = [
    {
      name: "Flowrate",
      value: summary.averages.avg_flowrate?.toFixed(2) || "N/A",
    },
    {
      name: "Pressure",
      value: summary.averages.avg_pressure?.toFixed(2) || "N/A",
    },
    {
      name: "Temperature",
      value: summary.averages.avg_temperature?.toFixed(2) || "N/A",
    },
  ];

  // --- 2. Prepare Data for Pie Chart ---
  const typeDistribution = summary.type_distribution;
  const pieData = {
    labels: Object.keys(typeDistribution),
    datasets: [
      {
        data: Object.values(typeDistribution),
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ],
        hoverBackgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ],
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: "Equipment Type Distribution",
        font: {
          size: 18,
        },
      },
    },
  };

  return (
    <div className="visualization">
      <h3>Analysis for: {summary.name}</h3>
      <div className="summary-layout">
        <div className="summary-box">
          <h4>Key Metrics</h4>
          <p>
            <strong>Total Equipment Count:</strong> {summary.total_count}
          </p>
          <h4>Average Values</h4>
          <table className="averages-table">
            <tbody>
              {averages.map((item) => (
                <tr key={item.name}>
                  <td>
                    <strong>Avg. {item.name}:</strong>
                  </td>
                  <td>{item.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="summary-box chart-container">
          <Pie data={pieData} options={pieOptions} />
        </div>
      </div>
    </div>
  );
};

export default DataVisualization;
