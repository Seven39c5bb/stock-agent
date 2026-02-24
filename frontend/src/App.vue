<template>
  <div class="min-h-screen px-6 py-10 md:px-12">
    <header class="max-w-5xl mx-auto mb-10">
      <div class="flex flex-col gap-4">
        <span class="font-display uppercase tracking-[0.3em] text-xs text-saffron">
          Stock Intel Agent
        </span>
        <h1 class="font-display text-4xl md:text-5xl leading-tight">
          让股票分析更清晰、可解释、可追溯
        </h1>
        <p class="text-base md:text-lg text-sand/80 max-w-3xl">
          输入股票名称或代码，系统将拉取最新行情与近30日走势，结合大模型给出结构化研究结论。
        </p>
      </div>
    </header>

    <section class="max-w-5xl mx-auto grid gap-6">
      <div class="glass rounded-3xl p-6 md:p-8 flex flex-col gap-6 fade-in">
        <div class="flex flex-col gap-2">
          <label class="text-sm uppercase tracking-[0.2em] text-sand/60 font-display">
            输入股票名称或代码
          </label>
          <div class="flex flex-col md:flex-row gap-3">
            <input
              v-model="query"
              class="input-shell flex-1 rounded-2xl px-4 py-3 text-base text-sand outline-none focus:ring-2 focus:ring-saffron"
              placeholder="如：贵州茅台 / 600519 / AAPL"
            />
            <button
              class="bg-saffron text-ink font-display px-6 py-3 rounded-2xl shadow-lg hover:shadow-xl transition"
              :disabled="loading"
              @click="handleAnalyze"
            >
              {{ loading ? "分析中..." : "开始分析" }}
            </button>
          </div>
          <p class="text-xs text-sand/60">
            数据非实时，仅供参考；结果不构成投资建议。
          </p>
        </div>

        <div v-if="error" class="text-rose text-sm">{{ error }}</div>
      </div>

      <div v-if="result" class="grid gap-6 md:grid-cols-3">
        <div class="glass rounded-3xl p-6 md:col-span-1 fade-in">
          <h2 class="font-display text-lg mb-4">概览</h2>
          <div class="space-y-4 text-sm">
            <div>
              <div class="text-sand/60">股票</div>
              <div class="text-lg font-display">{{ result.name }} ({{ result.symbol }})</div>
            </div>
            <div>
              <div class="text-sand/60">最新收盘价</div>
              <div class="text-2xl font-display">{{ result.data.spot.latest_price.toFixed(2) }}</div>
            </div>
            <div>
              <div class="text-sand/60">涨跌幅</div>
              <div :class="result.data.spot.change_pct >= 0 ? 'text-sea' : 'text-rose'">
                {{ result.data.spot.change_pct.toFixed(2) }}%
              </div>
            </div>
            <div>
              <div class="text-sand/60">波动率</div>
              <div>{{ result.data.metrics.vol_label }}</div>
            </div>
            <div>
              <div class="text-sand/60">趋势</div>
              <div>{{ result.data.metrics.trend_label }}</div>
            </div>
          </div>
        </div>

        <div class="glass rounded-3xl p-6 md:col-span-2 fade-in">
          <h2 class="font-display text-lg mb-4">智能体结论</h2>
          <div class="markdown prose prose-invert max-w-none" v-html="renderedMarkdown"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";

const query = ref("");
const loading = ref(false);
const error = ref("");
const result = ref(null);

const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const renderedMarkdown = computed(() => {
  if (!result.value?.markdown) {
    return "";
  }
  const html = marked.parse(result.value.markdown);
  return DOMPurify.sanitize(html);
});

const handleAnalyze = async () => {
  if (!query.value.trim()) {
    error.value = "请输入股票名称或代码";
    return;
  }

  loading.value = true;
  error.value = "";
  result.value = null;

  try {
    const response = await fetch(`${apiBase}/api/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query: query.value.trim() })
    });

    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.detail || "分析失败");
    }

    result.value = await response.json();
  } catch (err) {
    error.value = err.message || "分析失败";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.text-saffron {
  color: var(--saffron);
}

.text-sea {
  color: var(--sea);
}

.text-rose {
  color: var(--rose);
}

.bg-saffron {
  background-color: var(--saffron);
}
</style>
