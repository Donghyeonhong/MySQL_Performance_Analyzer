const experimentMap = {};

avgImprovementData.forEach(row => {
    const experimentId = row[0];
    const conditionId = row[2];
    const isIndexed = row[3];
    const executionTime = Number(row[4]);

    if (!experimentMap[experimentId]) {
        experimentMap[experimentId] = {
            before: null,
            after: []
        };
    }

    if (isIndexed === 0) {
        experimentMap[experimentId].before = executionTime;
    } else {
        experimentMap[experimentId].after.push({
            conditionId: conditionId,
            executionTime: executionTime
        });
    }
});

Object.values(experimentMap).forEach(experiment => {
    experiment.after.sort((a, b) => a.conditionId - b.conditionId);
});

const experimentIds = Object.keys(experimentMap).sort(
    (a, b) => Number(a) - Number(b)
);

const chartContainer = document.getElementById('analysis_performance_chart');

chartContainer.innerHTML = '';

experimentIds.forEach(id => {
    const chartSection = document.createElement('div');

    chartSection.id = `experiment_chart_${id}`;
    chartSection.style.width = '100%';
    chartSection.style.height = '300px';
    chartSection.style.marginBottom = '30px';

    chartContainer.appendChild(chartSection);
    const chart = echarts.init(chartSection);

    
    const experimentData = experimentMap[id];
    const categories = [
        'Before',
        ...experimentData.after.map((item, index) => `After ${index + 1}`)
    ];

    const values = [
        experimentData.before,
        ...experimentData.after.map(item => item.executionTime)
    ];
    
    const seriesData = [
        {
            label: {
                show: true,
                position: 'top',

                formatter: (params) => {
                    const executionTime = Number(params.value);

                    if (params.dataIndex === 0) {
                        return `{time|${executionTime.toFixed(2)} ms}`;
                    }

                    const improvementRate =
                        ((experimentData.before - executionTime) / experimentData.before) * 100;

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
            },
            itemStyle: {
                color: (params) => {
                    return params.dataIndex === 0 ? '#64748B' : '#14B8A6';
                },
                borderRadius: [5, 5, 0, 0]
            },
            name: 'Execution Time',
            type: 'bar',
            data: values
        }
    ];

    const option = {
        title: {
            text: `Experiment ${id}`,
            left: 'center',
            top: 5,
            textStyle: {
                color: '#F8FAFC',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        grid: {
            top: 65,
            left: 55,
            right: 30,
            bottom: 40,
            containLabel: true
        },
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            data: categories,
            axisLabel: {
                color: '#ffffff'
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

const xAxisData = experimentIds.map(
    id => `Experiment ${id}`
);

const beforeData = experimentIds.map(
    id => experimentMap[id].before
);

const maxAfterCount = Math.max(
    ...experimentIds.map(id => experimentMap[id].after.length)
);

const afterSeriesData = [];

for (let i = 0; i < maxAfterCount; i++) {
    const data = experimentIds.map(id => {
        return experimentMap[id].after[i]?.executionTime ?? null;
    });

    afterSeriesData.push(data);
}

console.log(xAxisData);
console.log(beforeData);
console.log(afterSeriesData);