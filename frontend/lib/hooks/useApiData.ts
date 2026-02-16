"use client";

import { useState, useEffect, useCallback } from "react";

interface UseApiDataOptions<T> {
  /** API取得関数 */
  fetcher: () => Promise<T>;
  /** API失敗時のフォールバックデータ */
  fallback?: T;
  /** 依存配列（変更時に再取得） */
  deps?: unknown[];
  /** 自動取得を無効化 */
  enabled?: boolean;
}

interface UseApiDataReturn<T> {
  data: T | undefined;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * API データ取得の共通フック
 * - マウント時に自動fetch
 * - ローディング/エラー状態管理
 * - フォールバックデータ対応（graceful degradation）
 */
export function useApiData<T>({
  fetcher,
  fallback,
  deps = [],
  enabled = true,
}: UseApiDataOptions<T>): UseApiDataReturn<T> {
  const [data, setData] = useState<T | undefined>(fallback);
  const [isLoading, setIsLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "データの取得に失敗しました";
      setError(message);
      // フォールバックデータがあればそのまま使用
      if (fallback && !data) {
        setData(fallback);
      }
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetcher]);

  useEffect(() => {
    if (enabled) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, ...deps]);

  return { data, isLoading, error, refetch: fetchData };
}
