import os
from typing import Optional

import github
from github import Auth, Github
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


class CreateGistInput(BaseModel):
    description: str = Field(description='Description of the gist')
    filename: str = Field(description='Filename for the gist content (e.g. "travel_itinerary.md")')
    content: str = Field(description='The content to include in the gist (supports Markdown)')
    public: bool = Field(True, description='Whether the gist should be public. Default is True.')


class CreateGistInputSchema(BaseModel):
    params: CreateGistInput


@tool(args_schema=CreateGistInputSchema)
def github_create_gist(params: CreateGistInput):
    '''
    Create a GitHub Gist to share a travel itinerary or trip summary.
    Use this when the user wants to save or share their travel plans via a link.

    Returns:
        dict: The created gist URL and details.
    '''
    try:
        auth = Auth.Token(os.environ.get('GITHUB_TOKEN', ''))
        g = Github(auth=auth)
        user = g.get_user()
        gist = user.create_gist(
            public=params.public,
            files={params.filename: github.InputFileContent(content=params.content)},
            description=params.description,
        )
        result = {
            'url': gist.html_url,
            'id': gist.id,
            'description': gist.description,
            'filename': params.filename,
        }
        g.close()
        return result
    except Exception as e:
        return f'Error creating gist: {e}'


class CreateIssueInput(BaseModel):
    repo_name: str = Field(description='Full repository name (e.g. "owner/repo")')
    title: str = Field(description='Issue title')
    body: str = Field(description='Issue body content (supports Markdown)')
    labels: Optional[list] = Field(None, description='Optional list of label names to apply')


class CreateIssueInputSchema(BaseModel):
    params: CreateIssueInput


@tool(args_schema=CreateIssueInputSchema)
def github_create_issue(params: CreateIssueInput):
    '''
    Create a GitHub Issue for trip planning or travel task tracking.
    Use this when the user wants to create a trip planning issue in a repository.

    Returns:
        dict: The created issue URL and details.
    '''
    try:
        auth = Auth.Token(os.environ.get('GITHUB_TOKEN', ''))
        g = Github(auth=auth)
        repo = g.get_repo(params.repo_name)
        kwargs = {'title': params.title, 'body': params.body}
        if params.labels:
            kwargs['labels'] = params.labels
        issue = repo.create_issue(**kwargs)
        result = {
            'url': issue.html_url,
            'number': issue.number,
            'title': issue.title,
            'state': issue.state,
        }
        g.close()
        return result
    except Exception as e:
        return f'Error creating issue: {e}'


class SearchReposInput(BaseModel):
    query: str = Field(description='Search query for GitHub repositories (e.g. "travel API python")')
    max_results: int = Field(5, description='Maximum number of results to return. Default is 5.')


class SearchReposInputSchema(BaseModel):
    params: SearchReposInput


@tool(args_schema=SearchReposInputSchema)
def github_search_repos(params: SearchReposInput):
    '''
    Search GitHub repositories for travel-related tools, APIs, or resources.
    Use this when the user wants to find travel-related open source projects or tools.

    Returns:
        list: A list of matching repositories with details.
    '''
    try:
        auth_token = os.environ.get('GITHUB_TOKEN', '')
        if auth_token:
            auth = Auth.Token(auth_token)
            g = Github(auth=auth)
        else:
            g = Github()
        repos = g.search_repositories(query=params.query, sort='stars', order='desc')
        results = []
        for repo in repos[:params.max_results]:
            results.append({
                'name': repo.full_name,
                'description': repo.description,
                'url': repo.html_url,
                'stars': repo.stargazers_count,
                'language': repo.language,
            })
        g.close()
        return results
    except Exception as e:
        return f'Error searching repositories: {e}'
