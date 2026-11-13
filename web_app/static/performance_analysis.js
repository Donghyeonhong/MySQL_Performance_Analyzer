const experimentMap = {};

avgImprovementData.forEach(row => {
    const experimentId = row[0];
    const queryId = row[1];
    const conditionId = row[2];
    const isIndexed = row[3];
    const executionTime = Number(row[4]);

    if (!experimentMap[experimentId]) {
        experimentMap[experimentId] = {};
    }

    if (!experimentMap[experimentId][queryId]) {
        experimentMap[experimentId][queryId] = {
            before: null,
            after: []
        };
    }

    const queryData = experimentMap[experimentId][queryId];

    if (isIndexed === 0) {
        queryData.before = executionTime;
    } else {
        queryData.after.push({
            conditionId: conditionId,
            executionTime: executionTime
        });
    }
});

Object.values(experimentMap).forEach(experiment => {
    Object.values(experiment).forEach(queryData => {
        queryData.after.sort((a, b) => a.conditionId - b.conditionId);
    });
});

const chartMap = {};

chartLabels.forEach((label, index) => {
    const [experimentName, queryLabel, conditionLabel] = label.split("\n");

    if (!chartMap[experimentName]) {
        chartMap[experimentName] = {};
    }

    if (!chartMap[experimentName][queryLabel]) {
        chartMap[experimentName][queryLabel] = {
            before: null,
            after: []
        };
    }

    const queryData = chartMap[experimentName][queryLabel];

    if (chartTypes[index] === "before") {
        queryData.before = chartValues[index];
    } else {
        queryData.after.push({
            conditionLabel: conditionLabel,
            executionTime: chartValues[index]
        });
    }
});

console.log(chartMap);

const experimentIds = Object.keys(experimentMap).sort(
    (a, b) => Number(a) - Number(b)
);

const chartContainer = document.getElementById('analysis_performance_chart');

chartContainer.innerHTML = '';

Object.keys(chartMap).forEach((experimentName, index) => {
    const chartSection = document.createElement('div');

    chartSection.id = `experiment_chart_${index}`;
    chartSection.style.width = '100%';
    chartSection.style.height = '350px';
    chartSection.style.marginBottom = '30px';

    chartContainer.appendChild(chartSection);

    const chart = echarts.init(chartSection);

    const experimentData = chartMap[experimentName];

    const categories = [];
    const values = [];

    Object.entries(experimentData).forEach(([queryLabel, queryData]) => {

        if (queryData.before === null) {
            return;
        }

        categories.push(`${queryLabel}\n미적용`);

        values.push({
            value: queryData.before,
            baseline: queryData.before,
            type: 'before'
        });

        queryData.after.forEach(item => {
            categories.push(`${queryLabel}\n${item.conditionLabel}`);

            values.push({
                value: item.executionTime,
                baseline: queryData.before,
                type: 'after'
            });
        });
    });

    const seriesData = [
        {
            name: 'Execution Time',
            type: 'bar',
            data: values,

            itemStyle: {
                color: (params) => {
                    return params.data.type === 'before'
                        ? '#64748B'
                        : '#14B8A6';
                },
                borderRadius: [5, 5, 0, 0]
            },

            label: {
                show: true,
                position: 'top',

                formatter: (params) => {
                    const executionTime = Number(params.value);
                    const baseline = params.data.baseline;

                    if (params.data.type === 'before') {
                        return `{time|${executionTime.toFixed(2)} ms}`;
                    }

                    const improvementRate =
                        ((baseline - executionTime) / baseline) * 100;

                    const status = improvementRate > 0
                        ? 'good'
                        : improvementRate < 0
                            ? 'bad'
                            : 'neutral';

                    const statusText = improvementRate > 0
                        ? '개선'
                        : improvementRate < 0
                            ? '악화'
                            : '변화 없음';

                    return `{time|${executionTime.toFixed(2)} ms}\n{${status}|(${Math.abs(improvementRate).toFixed(2)}% ${statusText})}`;
                },

                rich: {
                    time: {
                        color: '#F8FAFC',
                        fontSize: 11,
                        fontWeight: 'bold'
                    },
                    good: {
                        color: '#34D399',
                        fontSize: 11,
                        fontWeight: 'bold'
                    },
                    bad: {
                        color: '#F87171',
                        fontSize: 11,
                        fontWeight: 'bold'
                    },
                    neutral: {
                        color: '#94A3B8',
                        fontSize: 11,
                        fontWeight: 'bold'
                    }
                }
            }
        }
    ];

    const option = {
        title: {
            text: experimentName,
            left: 'center',
            top: 5,
            textStyle: {
                color: '#F8FAFC',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },

        grid: {
            top: 75,
            left: 55,
            right: 30,
            bottom: 65,
            containLabel: true
        },

        tooltip: {
            trigger: 'item',
            formatter: (params) => {
                return `<strong>${params.name}</strong><br/>Execution Time: ${Number(params.value).toFixed(2)} ms`;
            }
        },

        xAxis: {
            type: 'category',
            data: categories,
            axisLabel: {
                color: '#ffffff',
                interval: 0
            }
        },

        yAxis: {
            type: 'value',
            name: 'Execution Time (ms)',
            nameTextStyle: {
                color: '#94A3B8'
            },
            axisLabel: {
                color: '#CBD5E1'
            },
            axisLine: {
                show: true,
                lineStyle: {
                    color: '#475569'
                }
            },
            splitLine: {
                show: true,
                lineStyle: {
                    color: '#334155',
                    type: 'dashed'
                }
            }
        },
        series: seriesData
    };
    chart.setOption(option);
});

