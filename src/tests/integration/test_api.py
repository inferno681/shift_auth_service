import pytest


@pytest.mark.anyio
@pytest.mark.parametrize(
    'link',
    [
        pytest.param('registration_link', id='registration'),
        pytest.param('auth_link', id='login'),
    ],
    indirect=True,
)
async def test_registration_login(client, test_user, link):
    response = await client.post(link, json=test_user)
    assert response.status_code == 200
    assert 'token' in response.json()
    assert response.json()['token'] is not None


@pytest.mark.anyio
async def test_registration_existing_user(
    client, test_user, registration_link
):
    response = await client.post(registration_link, json=test_user)
    response = await client.post(registration_link, json=test_user)
