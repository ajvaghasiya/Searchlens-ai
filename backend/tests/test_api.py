def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_website_and_track_and_heatmap(client):
    create = client.post("/api/v1/websites", json={"domain": "example.com", "name": "Example"})
    assert create.status_code == 200
    website = create.json()
    website_id = website["id"]
    api_key = website["api_key"]

    track = client.post("/api/v1/track", json={
        "site_key": api_key,
        "events": [
            {"session_id": "s1", "page_url": "https://example.com/", "event_type": "pageview"},
            {"session_id": "s1", "page_url": "https://example.com/", "event_type": "click", "x_pct": 12.5, "y_pct": 30.0},
            {"session_id": "s1", "page_url": "https://example.com/", "event_type": "section_view", "section_id": "faq"},
        ],
    })
    assert track.status_code == 200
    assert track.json()["accepted"] == 3

    heatmap = client.get(f"/api/v1/websites/{website_id}/heatmap", params={"page_url": "https://example.com/"})
    assert heatmap.status_code == 200
    data = heatmap.json()
    assert len(data["click_grid"]) == 1
    assert data["section_engagement"][0]["section_id"] == "faq"


def test_geo_config_and_run_demo_mode(client):
    create = client.post("/api/v1/websites", json={"domain": "shop.example", "name": "Shop"})
    website_id = create.json()["id"]

    config = client.post(f"/api/v1/websites/{website_id}/geo/config", json={
        "brand_name": "Shop Co",
        "competitors": ["Rival Co"],
        "queries": ["best shop.example alternatives"],
    })
    assert config.status_code == 200

    run = client.post(f"/api/v1/websites/{website_id}/geo/run")
    assert run.status_code == 200
    assert len(run.json()) == 1  # one query x demo provider

    summary = client.get(f"/api/v1/websites/{website_id}/geo/summary")
    assert summary.status_code == 200
    assert "visibility_score" in summary.json()["summary"]
