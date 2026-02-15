// Azure Application Insights - サーバーサイド初期化は不要
// クライアントサイドは app/providers.tsx で初期化
export async function register() {
  // Next.js instrumentation hook
  // Application Insights のサーバーサイドテレメトリは
  // Backend (Python/FastAPI) 側で OpenTelemetry 経由で処理
}
