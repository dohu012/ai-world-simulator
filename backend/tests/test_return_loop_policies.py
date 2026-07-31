from datetime import UTC, datetime, time, timedelta

from app.domain.return_loop import (
    CausalClaim,
    EpistemicClass,
    NotificationCategory,
    NotificationPreferences,
    compile_summary,
    content_hash,
    decide_notification,
    safe_copy,
)


def claim(identifier: str, owner: str, visible: datetime, text: str = "Chen rejected the advice."):
    return CausalClaim(
        id=identifier,
        owner_id=owner,
        world_id="gray-harbor",
        source_type="action_result",
        source_id=f"source-{identifier}",
        source_version="1",
        source_hash=content_hash(identifier),
        occurred_at=visible - timedelta(minutes=1),
        visible_at=visible,
        epistemic_class=EpistemicClass.OUTCOME,
        text=text,
        agent_id="char-chen-mo",
        importance=0.9,
        schema_version="1.0",
    )


def test_summary_excludes_cross_owner_future_and_unsafe_claims() -> None:
    start = datetime(2026, 7, 1, tzinfo=UTC)
    end = start + timedelta(days=1)
    valid = claim("valid", "owner-a", start + timedelta(hours=1))
    summary = compile_summary(
        summary_id="summary-1",
        owner_id="owner-a",
        world_id="gray-harbor",
        interval_start=start,
        interval_end=end,
        claims=[
            valid,
            claim("private", "owner-b", start + timedelta(hours=2)),
            claim("future", "owner-a", end + timedelta(hours=1)),
            claim("unsafe", "owner-a", start + timedelta(hours=3), "Chen needs you. Urgent!"),
        ],
    )
    assert [item.id for item in summary.claims] == ["valid"]
    assert summary.narrative == ["[outcome] Chen rejected the advice."]
    assert (
        summary.source_watermark
        == compile_summary(
            summary_id="other",
            owner_id="owner-a",
            world_id="gray-harbor",
            interval_start=start,
            interval_end=end,
            claims=[valid],
        ).source_watermark
    )


def test_copy_taxonomy_rejects_pressure_in_english_and_chinese() -> None:
    assert safe_copy("Fictional world update: the rescue allocation is complete.")
    assert not safe_copy("We missed you. Chen needs you—act now!")
    assert not safe_copy("陈沫离不开你，必须回来")


def test_policy_defaults_to_no_push_and_enforces_follow_cap_pause() -> None:
    now = datetime(2026, 7, 1, 12, tzinfo=UTC)
    prefs = NotificationPreferences(owner_id="owner", world_id="gray-harbor")
    decision = decide_notification(
        category=NotificationCategory.MAJOR_OUTCOME,
        now=now,
        preferences=prefs,
        channel="push",
        sent_today=0,
        expiry=now + timedelta(days=1),
    )
    assert decision.reason == "CHANNEL_DISABLED"
    assert not decision.eligible

    prefs.push_enabled = True
    prefs.followed_agent_ids = {"char-lin"}
    decision = decide_notification(
        category=NotificationCategory.MAJOR_OUTCOME,
        now=now,
        preferences=prefs,
        channel="push",
        sent_today=0,
        expiry=now + timedelta(days=1),
        followed_agent_id="char-chen-mo",
    )
    assert decision.reason == "NOT_FOLLOWED"


def test_quiet_hours_are_timezone_aware_and_caps_never_bypass() -> None:
    now = datetime(2026, 11, 1, 5, 30, tzinfo=UTC)
    prefs = NotificationPreferences(
        owner_id="owner",
        world_id="gray-harbor",
        push_enabled=True,
        timezone="America/New_York",
        quiet_start=time(22),
        quiet_end=time(8),
    )
    deferred = decide_notification(
        category=NotificationCategory.ORACLE,
        now=now,
        preferences=prefs,
        channel="push",
        sent_today=0,
        expiry=now + timedelta(days=1),
        deadline=now + timedelta(minutes=30),
    )
    assert deferred.reason == "QUIET_DEFERRED"
    capped = decide_notification(
        category=NotificationCategory.ORACLE,
        now=now,
        preferences=prefs,
        channel="push",
        sent_today=1,
        expiry=now + timedelta(days=1),
        deadline=now + timedelta(minutes=30),
    )
    assert capped.reason == "DAILY_CAP"
    assert not capped.eligible
