console.log(window.chartData);

const chartDom = document.getElementById("performance_chart");
const myChart = echarts.init(chartDom);

const option = {
  title: {
    text: "Performance Comparison",
    left: "center",
    textStyle: {
      color: "#F8FAFC",
      fonsize: 16,
      fontWeight: "bold",
    },
  },

  legend: {
    top: 30,
    textStyle: {
      color: "#F8FAFC",
    },
  },

  tooltip: {
    trigger: "item",
    formatter: function(params) {
      return `
        <strong>${params.name}</strong><br/>
        Execution Time: ${params.value} ms
      `;
    }
  },

  xAxis: {
    type: "category",
    data: window.chartData.chart_labels,
  },

  yAxis: {
    type: "value",
    name: "Execution Time (ms)",
  },

  series: [
    {
      name: "Execution Time",
      type: "bar",
      data: window.chartData.chart_values.map((value, index) => ({
        value: value,
        itemStyle: {
          color: window.chartData.chart_types[index] === "before"
            ? "#38BDF8"
            : "#2563EB",
          borderRadius: [5, 5, 0, 0]
        }
      })),
    }
  ],
};

myChart.setOption(option);
