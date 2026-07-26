from httpx import AsyncClient

SPECIAL_AGENT_IDS = ["char-lin-zhixia", "char-zhou-qiming", "char-chen-mo"]


async def test_gray_harbor_demo_world_returns_fixed_payload(client: AsyncClient) -> None:
    response = await client.get("/demo/worlds/gray-harbor")

    assert response.status_code == 200
    body = response.json()
    for key in [
        "world",
        "characters",
        "agentProfiles",
        "events",
        "observations",
        "beliefs",
        "oracleRequests",
        "oracleResponses",
        "actionIntents",
        "actionResults",
    ]:
        assert key in body
    assert body["world"]["id"] == "world-gray-harbor-lockdown"
    assert len(body["characters"]) >= 3
    assert len(body["events"]) >= 5


async def test_gray_harbor_demo_world_does_not_use_database(client: AsyncClient) -> None:
    app = client._transport.app  # type: ignore[attr-defined]
    assert not hasattr(app.state, "database")

    response = await client.get("/demo/worlds/gray-harbor")

    assert response.status_code == 200
    assert not hasattr(app.state, "database")


async def test_gray_harbor_agent_perspective_returns_fixed_payload_for_each_agent(
    client: AsyncClient,
) -> None:
    for agent_id in SPECIAL_AGENT_IDS:
        response = await client.get(f"/demo/worlds/gray-harbor/agents/{agent_id}/perspective")

        assert response.status_code == 200
        body = response.json()
        for key in [
            "world",
            "character",
            "agentProfile",
            "observations",
            "beliefs",
            "oracleRequests",
            "oracleResponses",
            "actionIntents",
            "actionResults",
        ]:
            assert key in body
        assert body["character"]["id"] == agent_id
        assert body["agentProfile"]["character_id"] == agent_id
        assert set(body["world"]) == {
            "id",
            "name",
            "current_time",
            "schema_version",
            "version",
        }


async def test_gray_harbor_chen_perspective_includes_oracle_and_action_records(
    client: AsyncClient,
) -> None:
    response = await client.get("/demo/worlds/gray-harbor/agents/char-chen-mo/perspective")

    assert response.status_code == 200
    body = response.json()
    assert [request["id"] for request in body["oracleRequests"]] == [
        "oracle-request-chen-north-gate"
    ]
    assert [response["id"] for response in body["oracleResponses"]] == [
        "oracle-response-chen-north-gate"
    ]
    assert [intent["id"] for intent in body["actionIntents"]] == ["intent-chen-contact-courier"]
    assert [result["id"] for result in body["actionResults"]] == ["result-chen-contact-courier"]


async def test_gray_harbor_current_agent_perspective_uses_header_identity_for_lin(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/perspective",
        headers={"X-Demo-Agent-Id": "char-lin-zhixia"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["character"]["id"] == "char-lin-zhixia"
    assert body["character"]["name"] == "Lin Zhixia"
    assert all(observation["agent_id"] == "char-lin-zhixia" for observation in body["observations"])


async def test_gray_harbor_current_agent_perspective_chen_header_returns_chen_oracle(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/perspective",
        headers={"X-Demo-Agent-Id": "char-chen-mo"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["character"]["id"] == "char-chen-mo"
    assert [request["id"] for request in body["oracleRequests"]] == [
        "oracle-request-chen-north-gate"
    ]
    assert [intent["id"] for intent in body["actionIntents"]] == ["intent-chen-contact-courier"]


async def test_gray_harbor_current_agent_perspective_lin_header_excludes_chen_private_records(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/perspective",
        headers={"X-Demo-Agent-Id": "char-lin-zhixia"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["oracleRequests"] == []
    assert body["oracleResponses"] == []
    assert body["actionIntents"] == []
    assert body["actionResults"] == []
    assert "events" not in body
    assert "characters" not in body
    assert "agentProfiles" not in body
    assert all(observation["agent_id"] != "char-chen-mo" for observation in body["observations"])
    assert all(belief["agent_id"] != "char-chen-mo" for belief in body["beliefs"])


async def test_gray_harbor_current_agent_perspective_missing_header_returns_401(
    client: AsyncClient,
) -> None:
    response = await client.get("/demo/worlds/gray-harbor/me/perspective")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "DEMO_AGENT_ID_REQUIRED"


async def test_gray_harbor_current_agent_perspective_unknown_header_returns_403(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/perspective",
        headers={"X-Demo-Agent-Id": "char-unknown"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "DEMO_AGENT_FORBIDDEN"


async def test_gray_harbor_current_agent_input_returns_observation_only_feed_for_chen(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/input",
        headers={"X-Demo-Agent-Id": "char-chen-mo"},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"world", "character", "agentProfile", "observations"}
    assert body["character"]["id"] == "char-chen-mo"
    assert all(observation["agent_id"] == "char-chen-mo" for observation in body["observations"])
    oracle_observation = next(
        observation
        for observation in body["observations"]
        if observation["observation_type"] == "oracle"
    )
    assert oracle_observation["id"] == "obs-oracle-response-chen-north-gate"
    assert oracle_observation["observation_type"] == "oracle"
    assert oracle_observation["source_message_id"] == "oracle-response-chen-north-gate"
    assert oracle_observation["metadata"]["builder"] == "deterministic-v1"
    assert oracle_observation["metadata"]["advice_only"] is True
    assert "oracleRequests" not in body
    assert "oracleResponses" not in body
    assert "actionIntents" not in body
    assert "actionResults" not in body
    assert "beliefs" not in body
    assert "events" not in body


async def test_gray_harbor_current_agent_input_lin_excludes_chen_oracle_observation(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/input",
        headers={"X-Demo-Agent-Id": "char-lin-zhixia"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["character"]["id"] == "char-lin-zhixia"
    assert "obs-lin-fever" in [observation["id"] for observation in body["observations"]]
    assert all(observation["agent_id"] == "char-lin-zhixia" for observation in body["observations"])
    assert all(observation["observation_type"] != "oracle" for observation in body["observations"])


async def test_gray_harbor_current_agent_input_requires_demo_header(
    client: AsyncClient,
) -> None:
    response = await client.get("/demo/worlds/gray-harbor/me/input")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "DEMO_AGENT_ID_REQUIRED"


async def test_gray_harbor_current_agent_input_rejects_unknown_demo_header(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/demo/worlds/gray-harbor/me/input",
        headers={"X-Demo-Agent-Id": "char-unknown"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "DEMO_AGENT_FORBIDDEN"


async def test_gray_harbor_lin_perspective_excludes_chen_private_records(
    client: AsyncClient,
) -> None:
    response = await client.get("/demo/worlds/gray-harbor/agents/char-lin-zhixia/perspective")

    assert response.status_code == 200
    body = response.json()
    assert body["character"]["id"] == "char-lin-zhixia"
    assert all(observation["agent_id"] == "char-lin-zhixia" for observation in body["observations"])
    assert all(belief["agent_id"] == "char-lin-zhixia" for belief in body["beliefs"])
    assert body["oracleRequests"] == []
    assert body["oracleResponses"] == []
    assert body["actionIntents"] == []
    assert body["actionResults"] == []
    assert "events" not in body
    assert "characters" not in body
    assert "agentProfiles" not in body


async def test_gray_harbor_agent_perspective_unknown_agent_returns_404(
    client: AsyncClient,
) -> None:
    response = await client.get("/demo/worlds/gray-harbor/agents/char-unknown/perspective")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEMO_AGENT_NOT_FOUND"


async def test_gray_harbor_agent_perspective_does_not_use_database(
    client: AsyncClient,
) -> None:
    app = client._transport.app  # type: ignore[attr-defined]
    assert not hasattr(app.state, "database")

    response = await client.get("/demo/worlds/gray-harbor/agents/char-chen-mo/perspective")

    assert response.status_code == 200
    assert not hasattr(app.state, "database")
