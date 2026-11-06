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
    trigger: "axis",
    axisPointer: {
      type: "shadow",
    },
  },

  xAxis: {
    type: "category",
    data: window.chartData.labels,
  },

  yAxis: {
    type: "value",
    name: "Execution Time (ms)",
  },

  series: [
    {
      name: "Before Index",
      type: "bar",
      data: window.chartData.before,
      itemStyle: {
        color: "#38BDF8",
        borderRadius: [4, 4, 0, 0],
      },
    },
    {
      name: "After Index",
      type: "bar",
      data: window.chartData.after,
      itemStyle: {
        color: "#2563EB",
        borderRadius: [4, 4, 0, 0],
      },
    },
  ],
};

myChart.setOption(option);
