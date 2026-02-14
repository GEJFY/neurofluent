"""
FSRS（忘却曲線）アルゴリズム テスト
"""

from app.services.spaced_repetition import FSRS, FSRSCard


def test_new_card_defaults():
    """新規カードのデフォルト値"""
    card = FSRSCard()
    assert card.stability == 0.0
    assert card.difficulty == 0.0
    assert card.interval == 0
    assert card.repetitions == 0
    assert card.ease_factor == 2.5


def test_first_review_good():
    """初回レビュー（Good評価）で適切にスケジュールされること"""
    fsrs = FSRS()
    card = FSRSCard()
    result = fsrs.review(card, rating=3)  # Good
    assert result.stability > 0
    assert result.difficulty > 0
    assert result.interval >= 1
    assert result.repetitions == 1


def test_first_review_again():
    """初回レビュー（Again評価）で短いインターバルになること"""
    fsrs = FSRS()
    card = FSRSCard()
    result = fsrs.review(card, rating=1)  # Again
    assert result.interval <= 1
    assert result.repetitions == 0


def test_repeated_good_increases_interval():
    """連続Good評価でインターバルが伸びること"""
    fsrs = FSRS()
    card = FSRSCard()

    intervals = []
    for _ in range(5):
        card = fsrs.review(card, rating=3)
        intervals.append(card.interval)

    # インターバルは単調増加するはず
    for i in range(1, len(intervals)):
        assert intervals[i] >= intervals[i - 1]


def test_easy_gives_longer_interval():
    """Easy評価はGood評価より長いインターバルになること"""
    fsrs = FSRS()

    card_good = FSRSCard()
    card_good = fsrs.review(card_good, rating=3)

    card_easy = FSRSCard()
    card_easy = fsrs.review(card_easy, rating=4)

    assert card_easy.interval >= card_good.interval


def test_hard_gives_shorter_interval():
    """Hard評価はGood評価より短いインターバルになること"""
    fsrs = FSRS()

    card_good = FSRSCard()
    card_good = fsrs.review(card_good, rating=3)
    card_good = fsrs.review(card_good, rating=3)

    card_hard = FSRSCard()
    card_hard = fsrs.review(card_hard, rating=3)
    card_hard = fsrs.review(card_hard, rating=2)

    assert card_hard.interval <= card_good.interval


def test_retrievability():
    """記憶保持率の計算が正しいこと"""
    fsrs = FSRS()
    # stability=1の場合、t=0ではR≈1、t=stabilityではR<1
    r_0 = fsrs.retrievability(0, 1.0)
    r_1 = fsrs.retrievability(1, 1.0)
    assert abs(r_0 - 1.0) < 0.01
    assert r_1 < 1.0
    assert r_1 > 0.0
