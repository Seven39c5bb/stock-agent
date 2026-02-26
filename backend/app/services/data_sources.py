from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from typing import Any, Dict, List, Optional

import pandas as pd

from ..config import settings
from .llm_client import LLMClient


@dataclass
class SpotInfo:
    symbol: str
    name: str
    market: str
    latest_price: float
    change_pct: float
    volume: float
    industry: Optional[str]
    mode: str = "web_search"


_MARKET_CACHE: Dict[str, Dict[str, Any]] = {}
_SYMBOL_CACHE: Dict[str, Dict[str, Any]] = {}


def _normalize_query(query: str) -> str:
    return query.strip().upper()


def _extract_json_block(text: str) -> str:
    content = text.strip()
    if not content:
        raise ValueError("大模型返回为空")

    try:
        json.loads(content)
        return content
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", content, re.IGNORECASE)
    if fenced:
        return fenced.group(1)

    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        return content[start : end + 1]

    raise ValueError("大模型未返回有效JSON")


def _normalize_history(raw_history: Any, days: int) -> pd.DataFrame:
    if not isinstance(raw_history, list):
        raise ValueError("history 字段格式错误")

    rows: List[Dict[str, Any]] = []
    for item in raw_history:
        if not isinstance(item, dict):
            continue
        date = str(item.get("date", "")).strip()
        close = item.get("close")
        if not date:
            continue
        try:
            close_val = float(close)
        except (TypeError, ValueError):
            continue
        rows.append({"date": date, "close": close_val})

    if len(rows) < 10:
        raise ValueError("历史收盘数据不足，至少需要10个交易日")

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "close"]).sort_values("date")
    if df.empty:
        raise ValueError("历史数据解析失败")
    return df.tail(days)


def _build_search_prompt(query: str, days: int) -> str:
    today = datetime.today().strftime("%Y-%m-%d")
    return (
        "请使用你的联网搜索能力，查询真实可验证的股票行情信息。"
        "你必须只输出一个JSON对象，不允许输出任何解释文字。\n"
        f"查询对象: {query}\n"
        f"日期参考: {today}\n"
        f"历史范围: 最近 {days} 个交易日收盘价\n"
        "JSON结构必须严格如下:\n"
        "{\n"
        '  "symbol": "股票代码",\n'
        '  "name": "股票名称",\n'
        '  "market": "zh或us",\n'
        '  "industry": "行业(可为空字符串)",\n'
        '  "spot": {\n'
        '    "latest_price": 数字,\n'
        '    "change_pct": 数字,\n'
        '    "volume": 数字\n'
        "  },\n"
        '  "history": [\n'
        '    {"date": "YYYY-MM-DD", "close": 数字}\n'
        "  ]\n"
        "}\n"
        "要求:\n"
        "1) latest_price, change_pct, volume, history.close 必须为数字\n"
        "2) history 按日期升序，至少包含10条\n"
        "3) 若信息缺失，请尽力搜索，不要编造明显不合理值\n"
    )


def _fetch_market_payload(query: str, days: int = 30) -> Dict[str, Any]:
    normalized = _normalize_query(query)
    cache_key = f"{normalized}:{days}"
    if cache_key in _MARKET_CACHE:
        return _MARKET_CACHE[cache_key]

    llm = LLMClient(
        base_url=settings.search_llm_base_url,
        api_key=settings.search_llm_api_key,
        model=settings.search_llm_model,
        temperature=settings.search_llm_temperature,
        timeout=settings.search_llm_timeout,
    )
    if not llm.is_enabled():
        raise ValueError("LLM_API_KEY 未配置，无法使用联网搜索取数")

    system_prompt = "你是金融数据助手。必须先联网搜索，再返回严格JSON。"
    user_prompt = _build_search_prompt(query=normalized, days=days)
    
    search_mode = "web_search"
    try:
        raw = llm.chat_with_web_search(system_prompt, user_prompt)
    except RuntimeError as exc:
        raise ValueError(f"联网模式调用失败：{exc}") from exc
    if not raw:
        raise ValueError("联网模式调用失败：当前模型或网关不支持 web_search_preview，请更换支持 Responses+Web Search 的模型/渠道")

    payload = json.loads(_extract_json_block(raw))
    if not isinstance(payload, dict):
        raise ValueError("大模型返回格式错误")

    symbol = str(payload.get("symbol", "")).strip().upper()
    name = str(payload.get("name", "")).strip()
    market = str(payload.get("market", "")).strip().lower()
    if market not in {"zh", "us"}:
        market = "zh"

    spot = payload.get("spot", {})
    if not isinstance(spot, dict):
        raise ValueError("spot 字段格式错误")

    try:
        latest_price = float(spot.get("latest_price", 0) or 0)
        change_pct = float(spot.get("change_pct", 0) or 0)
        volume = float(spot.get("volume", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("spot 数值字段解析失败") from exc

    history_df = _normalize_history(payload.get("history", []), days=days)
    industry_raw = payload.get("industry")
    industry = str(industry_raw).strip() if industry_raw is not None else None

    if not symbol:
        symbol = normalized
    if not name:
        name = normalized

    normalized_payload = {
        "symbol": symbol,
        "name": name,
        "market": market,
        "industry": industry or None,
        "spot": {
            "latest_price": latest_price,
            "change_pct": change_pct,
            "volume": volume,
        },
        "history_df": history_df,
        "mode": search_mode
    }

    _MARKET_CACHE[cache_key] = normalized_payload
    _SYMBOL_CACHE[symbol] = normalized_payload
    return normalized_payload


def get_spot_info(query: str) -> SpotInfo:
    payload = _fetch_market_payload(query, days=30)
    return SpotInfo(
        symbol=payload["symbol"],
        name=payload["name"],
        market=payload["market"],
        latest_price=float(payload["spot"]["latest_price"]),
        change_pct=float(payload["spot"]["change_pct"]),
        volume=float(payload["spot"]["volume"]),
        industry=payload.get("industry"),
        mode=payload.get("mode", "web_search")
    )


def get_history(market: str, symbol: str, days: int = 30) -> pd.DataFrame:
    cached = _SYMBOL_CACHE.get(symbol.upper())
    if cached is None:
        cached = _fetch_market_payload(symbol, days=days)

    df = cached["history_df"].copy()
    if market in {"zh", "us"}:
        return df.tail(days)
    return df.tail(days)


def to_serializable(df: pd.DataFrame) -> Dict[str, list]:
    return {
        "date": df["date"].astype(str).tolist(),
        "close": df["close"].astype(float).round(4).tolist(),
    }
