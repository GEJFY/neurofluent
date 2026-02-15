"""復習(Review)ルーターのテスト - 間隔反復学習"""

import uuid
from datetime import UTC, datetime

import pytest

from app.models.review import ReviewItem


class TestReviewRouter:
    """Reviewルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_due_items_empty(self, auth_client):
        """復習アイテムがない場合は空リストを返す"""
        response = await auth_client.get("/api/review/due")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_due_items_with_data(self, auth_client, db_session, test_user):
        """復習対象アイテムの取得"""
        # テスト用の復習アイテムを作成
        item = ReviewItem(
            user_id=test_user.id,
            item_type="flash_translation",
            content={
                "target": "Let's schedule a meeting.",
                "user_answer": "Let's do a meeting.",
            },
            next_review_at=datetime.now(UTC),
        )
        db_session.add(item)
        await db_session.commit()

        response = await auth_client.get("/api/review/due")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["item_type"] == "flash_translation"
        assert "target" in data[0]["content"]

    @pytest.mark.asyncio
    async def test_complete_review(self, auth_client, db_session, test_user):
        """復習完了でFSRSスケジュールが更新される"""
        # テスト用の復習アイテムを作成
        item = ReviewItem(
            user_id=test_user.id,
            item_type="vocabulary",
            content={"word": "quarterly", "meaning": "四半期の"},
            next_review_at=datetime.now(UTC),
        )
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)

        response = await auth_client.post(
            "/api/review/complete",
            json={
                "item_id": str(item.id),
                "rating": 3,  # Good
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "next_review_at" in data
        assert data["new_interval_days"] >= 1
        assert data["new_ease_factor"] > 0

    @pytest.mark.asyncio
    async def test_complete_review_not_found(self, auth_client):
        """存在しない復習アイテムIDで404エラー"""
        fake_id = str(uuid.uuid4())

        response = await auth_client.post(
            "/api/review/complete",
            json={
                "item_id": fake_id,
                "rating": 3,
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_review_invalid_rating(self, auth_client):
        """不正なrating値でバリデーションエラー"""
        fake_id = str(uuid.uuid4())

        response = await auth_client.post(
            "/api/review/complete",
            json={
                "item_id": fake_id,
                "rating": 5,  # 最大は4
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーは401/403エラー（HTTPBearer）"""
        response = await client.get("/api/review/due")
        assert response.status_code in (401, 403)
