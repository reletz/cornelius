"""
GitHub integration service for syncing notes.
"""
import logging
from typing import List, Optional, Dict
from github import Github, GithubException

logger = logging.getLogger(__name__)


class GitHubService:
    """Handles GitHub repository synchronization."""
    
    def __init__(self, pat: str):
        """Initialize with Personal Access Token."""
        self.client = Github(pat)
        self._user = None
    
    @property
    def user(self):
        if self._user is None:
            self._user = self.client.get_user()
        return self._user
    
    def validate_connection(self) -> Dict[str, str]:
        """Validate PAT and return user info."""
        try:
            return {
                "valid": True,
                "username": self.user.login,
                "name": self.user.name or self.user.login
            }
        except GithubException as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_repo(self, repo_name: str):
        """Get repository by name (format: owner/repo)."""
        try:
            return self.client.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Failed to get repo {repo_name}: {e}")
            raise
    
    def push_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str
    ) -> bool:
        """
        Push or update a file in the repository.
        
        Args:
            repo_name: Repository in format owner/repo
            file_path: Path within the repository
            content: File content
            commit_message: Commit message
            
        Returns:
            True if successful
        """
        try:
            repo = self.get_repo(repo_name)
            
            # Check if file exists
            try:
                existing = repo.get_contents(file_path)
                # Update existing file
                repo.update_file(
                    file_path,
                    commit_message,
                    content,
                    existing.sha
                )
            except GithubException:
                # Create new file
                repo.create_file(
                    file_path,
                    commit_message,
                    content
                )
            
            return True
            
        except GithubException as e:
            logger.error(f"Failed to push file {file_path}: {e}")
            raise
    
    def sync_notes(
        self,
        repo_name: str,
        base_path: str,
        notes: List[Dict[str, str]]
    ) -> List[str]:
        """
        Sync multiple notes to repository.
        
        Args:
            repo_name: Repository in format owner/repo
            base_path: Base directory path in repo
            notes: List of dicts with 'filename' and 'content'
            
        Returns:
            List of synced file paths
        """
        synced = []
        
        for note in notes:
            file_path = f"{base_path}/{note['filename']}"
            try:
                self.push_file(
                    repo_name,
                    file_path,
                    note['content'],
                    f"Update Cornell notes: {note['filename']}"
                )
                synced.append(file_path)
            except Exception as e:
                logger.error(f"Failed to sync {file_path}: {e}")
        
        return synced
