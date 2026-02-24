from __future__ import annotations

from typing import Any, Dict

import numpy as np

from ..config import settings
from .data_sources import SpotInfo, get_history, get_spot_info, to_serializable
from .indicators import calc_slope, calc_support_resistance, calc_volatility
from .llm_client import LLMClient


def _trend_label(slope: float) -> str:
    if slope > 0.02:
        return "震荡上行"
    if slope < -0.02:
        return "震荡下行"
    return "区间震荡"


def _vol_label(volatility: float) -> str:
    if volatility >= 0.35:
        return "高波动"
    if volatility >= 0.2:
        return "中等波动"
    return "低波动"


def _build_llm_prompt(spot: SpotInfo, metrics: Dict[str, Any]) -> str:
    return (
        "请基于以下真实数据生成结构化投资参考，严格使用 Markdown 格式输出，"
        "并按指定的五个模块标题组织内容。\n"
        "模块标题必须使用：\n"
        "一、股票公司基本概况\n"
        "二、最新价格\n"
        "三、近一月走势分析\n"
        "四、长期投资价值\n"
        "五、10万模拟投资策略\n\n"
        f"股票：{spot.name} ({spot.symbol})\n"
        f"市场：{spot.market}\n"
        f"最新价：{spot.latest_price}\n"
        f"涨跌幅：{spot.change_pct}%\n"
        f"成交量：{spot.volume}\n"
        f"行业：{spot.industry or '未知'}\n"
        f"近30日趋势：{metrics['trend_label']}\n"
        f"趋势斜率：{metrics['slope']:.4f}\n"
        f"波动率：{metrics['volatility']:.4f}\n"
        f"支撑位：{metrics['support']:.2f}\n"
        f"压力位：{metrics['resistance']:.2f}\n"
        f"风险提示：数据非实时，仅供参考，不构成投资建议。\n"
    )


def _fallback_markdown(spot: SpotInfo, metrics: Dict[str, Any]) -> str:
    return (
        f"一、股票公司基本概况\n"
        f"- 股票名称：{spot.name}（{spot.symbol}）\n"
        f"- 所属行业：{spot.industry or '未知'}\n"
        f"- 提示：数据非实时，仅供参考。\n\n"
        f"二、最新价格\n"
        f"- 上一交易日收盘价：{spot.latest_price:.2f}\n"
        f"- 涨跌幅：{spot.change_pct:.2f}%\n\n"
        f"三、近一月走势分析\n"
        f"- 走势判断：{metrics['trend_label']}\n"
        f"- 支撑位/压力位：{metrics['support']:.2f} / {metrics['resistance']:.2f}\n"
        f"- 波动特征：{metrics['vol_label']}\n\n"
        f"四、长期投资价值\n"
        f"- 估值提示：需结合PE/PB/ROE等财务指标进一步判断。\n"
        f"- 风险提示：短期波动可能加大。\n\n"
        f"五、10万模拟投资策略\n"
        f"- 建仓比例：3:4:3 分批建仓\n"
        f"- 持有周期：3-12个月滚动观察\n"
        f"- 止损建议：跌破支撑位 3%-5%\n"
    )


def analyze_stock(query: str) -> Dict[str, Any]:
    spot = get_spot_info(query)
    history = get_history(spot.market, spot.symbol)
    closes = history["close"].astype(float).to_numpy()

    slope = calc_slope(closes)
    volatility = calc_volatility(closes)
    support, resistance = calc_support_resistance(closes)

    metrics = {
        "slope": slope,
        "volatility": volatility,
        "support": support,
        "resistance": resistance,
        "trend_label": _trend_label(slope),
        "vol_label": _vol_label(volatility),
    }

    llm = LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout,
    )

    system_prompt = "你是严谨的股票研究助理，禁止编造任何事实。"
    user_prompt = _build_llm_prompt(spot, metrics)

    markdown = llm.chat(system_prompt, user_prompt)
    if not markdown:
        markdown = _fallback_markdown(spot, metrics)

    return {
        "symbol": spot.symbol,
        "name": spot.name,
        "markdown": markdown,
        "mode": spot.mode,
        "data": {
            "spot": {
                "latest_price": spot.latest_price,
                "change_pct": spot.change_pct,
                "volume": spot.volume,
                "industry": spot.industry,
            },
            "history": to_serializable(history),
            "metrics": metrics,
        },
    }
