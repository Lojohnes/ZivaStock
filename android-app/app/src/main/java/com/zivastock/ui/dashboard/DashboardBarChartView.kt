package com.zivastock.ui.dashboard

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.View
import androidx.core.content.ContextCompat
import com.zivastock.R

class DashboardBarChartView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val barPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val labelPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.text_secondary)
        textSize = context.resources.getDimension(R.dimen.chart_label_text)
        textAlign = Paint.Align.CENTER
    }
    private val valuePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.text_primary)
        textSize = context.resources.getDimension(R.dimen.chart_value_text)
        textAlign = Paint.Align.CENTER
    }
    private val axisPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.divider)
        strokeWidth = 2f
    }

    private var data: DashboardChartData = DashboardChartData(emptyList())
    private var maxValue: Float = 1f

    fun setData(data: DashboardChartData) {
        this.data = data
        maxValue = data.groups.flatMap { it.bars.map { bar -> bar.value } }.maxOrNull() ?: 1f
        if (maxValue == 0f) maxValue = 1f
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        if (data.groups.isEmpty()) return

        val padding = resources.getDimension(R.dimen.chart_padding)
        val bottomLabelHeight = resources.getDimension(R.dimen.chart_bottom_label_height)
        val topValueHeight = resources.getDimension(R.dimen.chart_top_value_height)
        val groupSpacing = resources.getDimension(R.dimen.chart_group_spacing)
        val barSpacing = resources.getDimension(R.dimen.chart_bar_spacing)

        val chartTop = padding + topValueHeight
        val chartBottom = height - padding - bottomLabelHeight
        val chartHeight = chartBottom - chartTop

        val usableWidth = width - 2 * padding
        val groupCount = data.groups.size
        val totalBarCount = data.groups.sumOf { it.bars.size }

        val groupSlotWidth = if (groupCount > 0) {
            (usableWidth - (groupCount - 1) * groupSpacing) / groupCount
        } else usableWidth

        canvas.drawLine(padding, chartBottom, width - padding, chartBottom, axisPaint)

        var currentX = padding
        data.groups.forEach { group ->
            val barsWidth = groupSlotWidth - (group.bars.size - 1) * barSpacing
            val barWidth = barsWidth / group.bars.size

            group.bars.forEachIndexed { index, bar ->
                val barHeight = (bar.value / maxValue) * chartHeight
                val left = currentX + index * (barWidth + barSpacing)
                val top = chartBottom - barHeight
                val right = left + barWidth
                val bottom = chartBottom

                barPaint.color = bar.color
                canvas.drawRoundRect(
                    RectF(left, top, right, bottom),
                    barWidth / 8,
                    barWidth / 8,
                    barPaint
                )

                if (bar.value > 0) {
                    canvas.drawText(
                        bar.value.toInt().toString(),
                        left + barWidth / 2,
                        top - valuePaint.fontMetrics.descent,
                        valuePaint
                    )
                }
            }

            canvas.drawText(
                group.label,
                currentX + groupSlotWidth / 2,
                chartBottom + bottomLabelHeight / 2 - labelPaint.fontMetrics.ascent / 2,
                labelPaint
            )

            currentX += groupSlotWidth + groupSpacing
        }
    }
}
