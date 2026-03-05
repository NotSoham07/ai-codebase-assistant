import requests
from openai import OpenAI
from app.settings import settings


def fetch_pr_diff(pr_url: str):

    try:
        # Convert PR URL to diff URL
        # Example:
        # https://github.com/tiangolo/fastapi/pull/10975
        # ->
        # https://github.com/tiangolo/fastapi/pull/10975.diff

        if not pr_url.endswith(".diff"):
            diff_url = pr_url + ".diff"
        else:
            diff_url = pr_url

        headers = {
            "User-Agent": "ai-codebase-assistant"
        }

        response = requests.get(diff_url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"GitHub returned {response.status_code}")

        return response.text

    except Exception as e:
        raise Exception(f"Failed to fetch PR diff: {str(e)}")


def review_pull_request(pr_url: str):

    diff = fetch_pr_diff(pr_url)

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url
    )

    prompt = f"""
You are a senior software engineer reviewing a pull request.

Analyze this diff and provide:

- possible bugs
- code quality issues
- performance concerns
- suggested improvements

PR DIFF:

{diff[:12000]}
"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content