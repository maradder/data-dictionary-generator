import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Tooltip as UITooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { InfoModal } from '@/components/common/InfoModal'
import type { Field } from '@/types/api'

interface FieldStatisticsProps {
  field: Field
}

const COLORS = {
  primary: '#3b82f6', // blue-500
  secondary: '#8b5cf6', // violet-500
  success: '#10b981', // green-500
  warning: '#f59e0b', // amber-500
  danger: '#ef4444', // red-500
  null: '#94a3b8', // slate-400
  valid: '#10b981', // green-500
}

export function FieldStatistics({ field }: FieldStatisticsProps) {
  // Check if field has numeric statistics
  const hasNumericStats =
    field.min_value !== null ||
    field.max_value !== null ||
    field.mean_value !== null

  // Check if field has sample values that could indicate categorical data
  const hasSampleValues = field.sample_values && field.sample_values.length > 0

  // Generate null percentage pie chart data
  const nullPercentageData = useMemo(() => {
    const nullPct = field.null_percentage ?? 0
    const validPercentage = 100 - nullPct
    return [
      { name: 'Valid Values', value: validPercentage, count: field.total_count - field.null_count },
      { name: 'Null Values', value: nullPct, count: field.null_count },
    ]
  }, [field.null_percentage, field.null_count, field.total_count])

  // Generate box plot data for quartiles
  const boxPlotData = useMemo(() => {
    if (!field.percentile_25 || !field.percentile_75) return null

    return {
      min: field.min_value || 0,
      q1: field.percentile_25,
      median: field.percentile_50 || field.median_value || 0,
      q3: field.percentile_75,
      max: field.max_value || 0,
    }
  }, [field])

  // Generate histogram bins from sample values (simplified approach)
  const histogramData = useMemo(() => {
    if (!hasNumericStats || !field.sample_values || field.sample_values.length === 0) {
      return null
    }

    // Filter numeric values
    const numericValues = field.sample_values
      .filter((val) => typeof val === 'number' && !isNaN(val))
      .map(Number)

    if (numericValues.length === 0) return null

    // Create bins
    const min = field.min_value || Math.min(...numericValues)
    const max = field.max_value || Math.max(...numericValues)
    const binCount = 10
    const binSize = (max - min) / binCount

    if (binSize === 0) {
      // All values are the same
      return [
        {
          bin: min.toFixed(2),
          count: numericValues.length,
          range: `${min.toFixed(2)}`,
        },
      ]
    }

    const bins = Array.from({ length: binCount }, (_, i) => ({
      bin: `${(min + i * binSize).toFixed(2)}`,
      count: 0,
      range: `${(min + i * binSize).toFixed(2)} - ${(min + (i + 1) * binSize).toFixed(2)}`,
    }))

    // Count values in each bin
    numericValues.forEach((value) => {
      const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1)
      bins[binIndex].count++
    })

    return bins.filter((bin) => bin.count > 0)
  }, [field, hasNumericStats])

  // Generate categorical frequency data from sample values
  const categoryFrequencyData = useMemo(() => {
    if (!hasSampleValues || hasNumericStats) return null

    // Count occurrences of each value
    const frequencyMap = new Map<string, number>()
    field.sample_values!.forEach((value) => {
      const key = JSON.stringify(value)
      frequencyMap.set(key, (frequencyMap.get(key) || 0) + 1)
    })

    // Convert to array and sort by frequency
    return Array.from(frequencyMap.entries())
      .map(([value, count]) => ({
        value: value.replace(/^"|"$/g, ''), // Remove quotes
        count,
        percentage: ((count / field.sample_values!.length) * 100).toFixed(1),
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10) // Top 10 values
  }, [field, hasSampleValues, hasNumericStats])

  // If no statistics are available
  if (!hasNumericStats && !hasSampleValues) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Statistics</CardTitle>
          <CardDescription>No statistical data available for this field</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Statistical visualizations are available for numeric and categorical fields with sample data.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Null Percentage Pie Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle>Data Completeness</CardTitle>
              <InfoModal title="Understanding Data Completeness">
                <div className="space-y-4">
                  <p>
                    Data completeness shows the proportion of null (missing) versus valid (populated)
                    values in this field.
                  </p>
                  <div className="space-y-2">
                    <h4 className="font-medium">Interpreting the Chart</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      <li><strong className="text-green-600">Valid Values</strong> - Non-null entries that contain data</li>
                      <li><strong className="text-slate-500">Null Values</strong> - Missing or empty entries</li>
                    </ul>
                  </div>
                  <div className="bg-muted p-3 rounded-md">
                    <p className="font-medium mb-1">What High Null Percentages Mean</p>
                    <p className="text-sm">
                      High null percentages (&gt;50%) may indicate:
                    </p>
                    <ul className="list-disc list-inside space-y-1 text-sm mt-1">
                      <li>Optional fields that users rarely fill in</li>
                      <li>Data quality issues in the collection process</li>
                      <li>Recent additions to the schema with incomplete backfill</li>
                    </ul>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Fields with high null percentages may need special handling in your application logic.
                  </p>
                </div>
              </InfoModal>
            </div>
            <TooltipProvider>
              <UITooltip>
                <TooltipTrigger asChild>
                  <Badge variant="outline">
                    {(100 - (field.null_percentage ?? 0)).toFixed(1)}% Complete
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Percentage of non-null values in this field</p>
                </TooltipContent>
              </UITooltip>
            </TooltipProvider>
          </div>
          <CardDescription>Distribution of null vs valid values</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={nullPercentageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(props: { name?: string; value?: number }) =>
                  props.name && props.value !== undefined
                    ? `${props.name}: ${props.value.toFixed(1)}%`
                    : ''
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {nullPercentageData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={index === 0 ? COLORS.valid : COLORS.null}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, _name: string, props: { payload?: { count: number } }) =>
                  `${value.toFixed(1)}% (${props.payload?.count.toLocaleString() || 0} records)`
                }
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Histogram for Numeric Fields */}
      {histogramData && histogramData.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CardTitle>Value Distribution</CardTitle>
              <InfoModal title="Understanding Value Distribution">
                <div className="space-y-4">
                  <p>
                    The histogram shows how numeric values are distributed across different ranges.
                    Each bar represents a range (bin) of values and its height shows how many values
                    fall within that range.
                  </p>
                  <div className="space-y-2">
                    <h4 className="font-medium">Reading the Chart</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      <li><strong>X-axis</strong> - Value ranges (bins) from minimum to maximum</li>
                      <li><strong>Y-axis</strong> - Count of values in each range</li>
                      <li><strong>Bar height</strong> - More values in that range means taller bar</li>
                    </ul>
                  </div>
                  <div className="bg-muted p-3 rounded-md">
                    <p className="font-medium mb-1">Common Patterns</p>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      <li><strong>Normal distribution</strong> - Bell-shaped curve with peak in middle</li>
                      <li><strong>Skewed distribution</strong> - Peak on one side with long tail</li>
                      <li><strong>Uniform distribution</strong> - Roughly equal heights across all bins</li>
                      <li><strong>Bimodal distribution</strong> - Two distinct peaks</li>
                    </ul>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    This visualization helps identify outliers, data quality issues, and the typical
                    range of values in your field.
                  </p>
                </div>
              </InfoModal>
            </div>
            <CardDescription>
              Histogram showing the distribution of numeric values (from sample data)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={histogramData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="bin"
                  className="text-xs"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis className="text-xs" />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="bg-background border rounded-lg p-2 shadow-lg">
                          <p className="text-sm font-medium">Range: {data.range}</p>
                          <p className="text-sm text-muted-foreground">
                            Count: {data.count} values
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="count" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Box Plot for Quartiles */}
      {boxPlotData && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CardTitle>Quartile Analysis</CardTitle>
              <InfoModal title="Understanding Quartile Analysis">
                <div className="space-y-4">
                  <p>
                    Quartile analysis divides your data into four equal parts, providing a
                    five-number summary that reveals the spread and central tendency of your values.
                  </p>
                  <div className="space-y-2">
                    <h4 className="font-medium">The Five Numbers</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      <li><strong>Minimum</strong> - The smallest value in the dataset</li>
                      <li><strong>Q1 (25th percentile)</strong> - 25% of values are below this point</li>
                      <li><strong>Median (50th percentile)</strong> - The middle value; half above, half below</li>
                      <li><strong>Q3 (75th percentile)</strong> - 75% of values are below this point</li>
                      <li><strong>Maximum</strong> - The largest value in the dataset</li>
                    </ul>
                  </div>
                  <div className="bg-muted p-3 rounded-md">
                    <p className="font-medium mb-1">Interquartile Range (IQR)</p>
                    <p className="text-sm">
                      The range between Q1 and Q3 contains the middle 50% of your data.
                      A larger IQR indicates more spread in your values, while a smaller IQR
                      means values are more concentrated around the median.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium">Identifying Outliers</h4>
                    <p className="text-sm">
                      Values significantly outside the Q1-Q3 range (typically beyond 1.5 × IQR)
                      are considered outliers and may represent unusual data points, errors,
                      or genuinely extreme values that need attention.
                    </p>
                  </div>
                </div>
              </InfoModal>
            </div>
            <CardDescription>
              Five-number summary (min, Q1, median, Q3, max)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Visual Box Plot */}
              <div className="relative h-24 px-8">
                {/* Min-Max line */}
                <div
                  className="absolute top-1/2 left-8 right-8 h-0.5 bg-muted-foreground"
                  style={{ transform: 'translateY(-50%)' }}
                />

                {/* Box (Q1 to Q3) */}
                <div
                  className="absolute top-1/4 h-1/2 border-2 border-primary bg-primary/10 rounded"
                  style={{
                    left: `calc(8% + ${((boxPlotData.q1 - boxPlotData.min) / (boxPlotData.max - boxPlotData.min)) * 84}%)`,
                    right: `calc(8% + ${((boxPlotData.max - boxPlotData.q3) / (boxPlotData.max - boxPlotData.min)) * 84}%)`,
                  }}
                />

                {/* Median line */}
                <div
                  className="absolute top-1/4 h-1/2 w-0.5 bg-destructive"
                  style={{
                    left: `calc(8% + ${((boxPlotData.median - boxPlotData.min) / (boxPlotData.max - boxPlotData.min)) * 84}%)`,
                  }}
                />

                {/* Min marker */}
                <div
                  className="absolute top-1/3 h-1/3 w-0.5 bg-muted-foreground"
                  style={{ left: '8%' }}
                />

                {/* Max marker */}
                <div
                  className="absolute top-1/3 h-1/3 w-0.5 bg-muted-foreground"
                  style={{ right: '8%' }}
                />
              </div>

              {/* Quartile Values */}
              <div className="grid grid-cols-5 gap-2 text-center">
                <TooltipProvider>
                  <UITooltip>
                    <TooltipTrigger asChild>
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground">Min</p>
                        <p className="text-sm font-semibold">{boxPlotData.min.toFixed(2)}</p>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Minimum value in the dataset</p>
                    </TooltipContent>
                  </UITooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <UITooltip>
                    <TooltipTrigger asChild>
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground">Q1</p>
                        <p className="text-sm font-semibold">{boxPlotData.q1.toFixed(2)}</p>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>25th percentile (first quartile)</p>
                    </TooltipContent>
                  </UITooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <UITooltip>
                    <TooltipTrigger asChild>
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-destructive">Median</p>
                        <p className="text-sm font-semibold text-destructive">
                          {boxPlotData.median.toFixed(2)}
                        </p>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>50th percentile (median)</p>
                    </TooltipContent>
                  </UITooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <UITooltip>
                    <TooltipTrigger asChild>
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground">Q3</p>
                        <p className="text-sm font-semibold">{boxPlotData.q3.toFixed(2)}</p>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>75th percentile (third quartile)</p>
                    </TooltipContent>
                  </UITooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <UITooltip>
                    <TooltipTrigger asChild>
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground">Max</p>
                        <p className="text-sm font-semibold">{boxPlotData.max.toFixed(2)}</p>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Maximum value in the dataset</p>
                    </TooltipContent>
                  </UITooltip>
                </TooltipProvider>
              </div>

              {/* IQR and Range */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">
                    Interquartile Range (IQR)
                  </p>
                  <p className="text-lg font-semibold">
                    {(boxPlotData.q3 - boxPlotData.q1).toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">Middle 50% of data spread</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Range</p>
                  <p className="text-lg font-semibold">
                    {(boxPlotData.max - boxPlotData.min).toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">Total data spread</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bar Chart for Categorical Values */}
      {categoryFrequencyData && categoryFrequencyData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Value Frequency</CardTitle>
            <CardDescription>
              Top {categoryFrequencyData.length} most common values (from sample data)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={categoryFrequencyData}
                layout="vertical"
                margin={{ left: 100, right: 30 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis type="number" className="text-xs" />
                <YAxis
                  type="category"
                  dataKey="value"
                  className="text-xs"
                  width={100}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="bg-background border rounded-lg p-2 shadow-lg">
                          <p className="text-sm font-medium">{data.value}</p>
                          <p className="text-sm text-muted-foreground">
                            Count: {data.count} ({data.percentage}%)
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="count" fill={COLORS.secondary} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Distribution Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Distribution Summary</CardTitle>
          <CardDescription>Key metrics about value distribution</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Distinct Values</p>
              <p className="text-2xl font-bold">{field.distinct_count.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">
                {((field.distinct_count / field.total_count) * 100).toFixed(1)}% of total
              </p>
            </div>
            {field.cardinality_ratio !== null && (
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">Cardinality</p>
                <p className="text-2xl font-bold">{field.cardinality_ratio.toFixed(4)}</p>
                <p className="text-xs text-muted-foreground">
                  {field.cardinality_ratio < 0.01
                    ? 'Low (repeating values)'
                    : field.cardinality_ratio > 0.95
                      ? 'High (mostly unique)'
                      : 'Medium'}
                </p>
              </div>
            )}
            {hasNumericStats && field.std_dev !== null && (
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">Std Deviation</p>
                <p className="text-2xl font-bold">{field.std_dev.toFixed(2)}</p>
                <p className="text-xs text-muted-foreground">Measure of variability</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
