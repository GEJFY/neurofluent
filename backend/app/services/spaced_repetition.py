"""間隔反復学習サービス - FSRSアルゴリズム実装

FSRS (Free Spaced Repetition Scheduler) の実装。
安定度(stability)と難易度(difficulty)に基づいて最適な復習間隔を計算する。

参考: https://github.com/open-spaced-repetition/fsrs4anki
"""

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass
class FSRSCard:
    """FSRSカードの状態を表すデータクラス"""

    stability: float = 1.0
    difficulty: float = 0.3
    interval: float = 0.0
    repetitions: int = 0
    ease_factor: float = 2.5
    next_review: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_review: datetime | None = None


class FSRS:
    """
    FSRSアルゴリズム - 間隔反復スケジューリング

    レーティング:
        1 = Again（もう一度）: 完全に忘れていた
        2 = Hard（難しい）: 思い出せたが困難だった
        3 = Good（良い）: 適度な努力で思い出せた
        4 = Easy（簡単）: 即座に思い出せた
    """

    def __init__(self):
        # FSRSパラメータ（デフォルト値、学習データで最適化可能）
        self.desired_retention: float = 0.9
        self.decay: float = -0.5
        # FSRS-4.5のデフォルトパラメータ
        self.initial_stability = [0.4, 0.9, 2.3, 6.0]

        # 重みパラメータ（w0〜w18）
        self.w = [
            0.4,  # w0: 初期安定度調整
            0.9,  # w1
            2.3,  # w2
            6.0,  # w3
            7.0,  # w4: 難易度の初期値影響
            0.5,  # w5: 難易度更新の平均回帰係数
            1.2,  # w6: 難易度更新のレーティング影響
            0.01,  # w7: 安定度成功時の基本増加率
            1.5,  # w8: 安定度と難易度の交互作用
            0.1,  # w9: 安定度に対する記憶度の影響
            1.0,  # w10: 安定度の自己参照係数
            2.0,  # w11: 失敗時の安定度減衰
            0.02,  # w12: 失敗時の難易度影響
            0.3,  # w13: 失敗時の安定度影響
            0.5,  # w14: Hard時の安定度ペナルティ
            2.0,  # w15: Easy時の安定度ボーナス
            0.2,  # w16: 記憶度の追加影響
            3.0,  # w17: 短期記憶の減衰
            0.7,  # w18: 追加パラメータ
        ]

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """値を指定範囲にクランプ"""
        return max(min_val, min(max_val, value))

    def _calculate_retrievability(self, stability: float, elapsed_days: float) -> float:
        """記憶度（retrievability）を計算

        R(t) = (1 + t / S) ^ decay
        ここで t=経過日数, S=安定度, decay=-0.5
        """
        if stability <= 0:
            return 0.0
        return (1 + elapsed_days / stability) ** self.decay

    def _calculate_interval(self, stability: float) -> float:
        """安定度から最適な復習間隔を計算

        interval = S * ((1/R)^(1/decay) - 1)
        ここで R=desired_retention, decay=-0.5
        """
        if stability <= 0:
            return 1.0
        interval = stability * ((1 / self.desired_retention) ** (1 / self.decay) - 1)
        return max(1.0, interval)

    def _initial_difficulty(self, rating: int) -> float:
        """初回レーティングから初期難易度を計算

        D0 = w4 - exp(w5 * (rating - 1)) + 1
        """
        d = self.w[4] - math.exp(self.w[5] * (rating - 1)) + 1
        return self._clamp(d, 0.1, 1.0)

    def _update_difficulty(self, difficulty: float, rating: int) -> float:
        """難易度を更新

        D' = w6 * D0(4) + (1 - w6) * (D - w7 * (rating - 3))
        平均回帰 + レーティングに基づく調整
        """
        d0_easy = self._initial_difficulty(4)
        new_d = self.w[5] * d0_easy + (1 - self.w[5]) * (
            difficulty - self.w[6] * (rating - 3)
        )
        return self._clamp(new_d, 0.1, 1.0)

    def _update_stability_success(
        self,
        stability: float,
        difficulty: float,
        retrievability: float,
        rating: int,
    ) -> float:
        """成功時の安定度更新（rating >= 2）

        S'_success = S * (
            1 + exp(w7) *
            (11 - D) *
            S^(-w8) *
            (exp(w9 * (1 - R)) - 1) *
            hard_penalty *
            easy_bonus
        )
        """
        hard_penalty = self.w[14] if rating == 2 else 1.0
        easy_bonus = self.w[15] if rating == 4 else 1.0

        new_s = stability * (
            1
            + math.exp(self.w[7])
            * (11 - difficulty * 10)  # 難易度を0〜1から0〜10にスケール
            * (stability ** (-self.w[8]))
            * (math.exp(self.w[9] * (1 - retrievability)) - 1)
            * hard_penalty
            * easy_bonus
        )

        return max(0.1, new_s)

    def _update_stability_fail(
        self,
        stability: float,
        difficulty: float,
        retrievability: float,
    ) -> float:
        """失敗時の安定度更新（rating == 1）

        S'_fail = w11 * D^(-w12) * ((S+1)^w13 - 1) * exp(w16 * (1 - R))
        """
        new_s = (
            self.w[11]
            * (difficulty * 10 + 0.1) ** (-self.w[12])
            * ((stability + 1) ** self.w[13] - 1)
            * math.exp(self.w[16] * (1 - retrievability))
        )

        # 失敗時の安定度は前回より小さくなるべき
        return max(0.1, min(new_s, stability))

    def review(
        self, card: FSRSCard, rating: int, elapsed_days: float | None = None
    ) -> FSRSCard:
        """
        復習結果に基づいてカード状態を更新

        Args:
            card: 現在のカード状態
            rating: ユーザーの評価（1=Again, 2=Hard, 3=Good, 4=Easy）
            elapsed_days: 前回の復習からの経過日数（Noneの場合は自動計算）

        Returns:
            更新後のFSRSCard
        """
        rating = self._clamp(rating, 1, 4)
        now = datetime.now(UTC)

        # 経過日数の計算
        if elapsed_days is None:
            if card.last_review is not None:
                delta = now - card.last_review
                elapsed_days = max(0, delta.total_seconds() / 86400)
            else:
                elapsed_days = 0

        if card.repetitions == 0:
            # 初回復習: 初期パラメータを設定
            card.stability = self.initial_stability[rating - 1]
            card.difficulty = self._initial_difficulty(rating)
        else:
            # 記憶度を計算
            retrievability = self._calculate_retrievability(
                card.stability, elapsed_days
            )

            if rating >= 2:
                # 成功（Hard, Good, Easy）
                card.stability = self._update_stability_success(
                    card.stability, card.difficulty, retrievability, rating
                )
            else:
                # 失敗（Again）
                card.stability = self._update_stability_fail(
                    card.stability, card.difficulty, retrievability
                )

            # 難易度を更新
            card.difficulty = self._update_difficulty(card.difficulty, rating)

        # 復習間隔を計算
        if rating == 1:
            # Again: 短い間隔で再復習
            card.interval = max(1.0, card.stability * 0.5)
        else:
            card.interval = self._calculate_interval(card.stability)

        # ease_factorを互換性のために更新（SM-2形式）
        ef_delta = 0.1 - (4 - rating) * (0.08 + (4 - rating) * 0.02)
        card.ease_factor = max(1.3, card.ease_factor + ef_delta)

        # 次回復習日とメタデータを更新
        card.repetitions += 1
        card.last_review = now
        card.next_review = now + timedelta(days=card.interval)

        return card


# シングルトンインスタンス
fsrs = FSRS()
