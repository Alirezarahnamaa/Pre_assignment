import requests
import time
from typing import List, Dict, Set

class CamelMetricsAnalyzer:
    def __init__(self, repo_owner="apache", repo_name="camel"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_base = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
    
    def search_commits_for_issue(self, issue_id: str) -> List[str]:
        query = f"{issue_id} repo:{self.repo_owner}/{self.repo_name}"
        url = f"{self.github_api_base}/search/commits"
        params = {"q": query, "per_page": 30}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                commits = response.json().get("items", [])
                return [commit["sha"] for commit in commits]
            return []
        except Exception:
            return []
    
    def get_commit_details(self, commit_sha: str) -> Dict:
        url = f"{self.github_api_base}/repos/{self.repo_owner}/{self.repo_name}/commits/{commit_sha}"
        try:
            response = requests.get(url, headers=self.headers)
            return response.json() if response.status_code == 200 else {}
        except Exception:
            return {}
    
    def calculate_dmm_metrics(self, commit_data: Dict) -> float:
        if not commit_data or "files" not in commit_data:
            return 0.0
        
        files = commit_data["files"]
        
        top_dirs = set()
        for file in files:
            parts = file["filename"].split('/')
            if len(parts) > 1:
                top_dirs.add(parts[0])
        cohesion = min(1.0, 1.0 / (len(top_dirs) + 0.5) if top_dirs else 1.0)
        
        coupling = min(1.0, 1.0 / (len(files) + 0.5))
        
        total_changes = sum(f.get("additions", 0) + f.get("deletions", 0) for f in files)
        complexity = min(1.0, 1.0 / (total_changes / 10 + 0.5) if total_changes > 0 else 1.0)
        
        return (cohesion + coupling + complexity) / 3.0
    
    def analyze_issues(self, issue_ids: List[str]) -> Dict:
        total_commits = 0
        total_files = 0
        total_dmm = 0.0
        issues_with_commits = 0
        
        for issue_id in issue_ids:
            commit_shas = self.search_commits_for_issue(issue_id)
            
            if not commit_shas:
                continue
            
            issues_with_commits += 1
            all_files = set()
            issue_dmm_total = 0.0
            
            for sha in commit_shas:
                commit_data = self.get_commit_details(sha)
                if commit_data:
                    for file in commit_data.get("files", []):
                        all_files.add(file["filename"])
                    issue_dmm_total += self.calculate_dmm_metrics(commit_data)
                time.sleep(0.5)
            
            total_commits += len(commit_shas)
            total_files += len(all_files)
            total_dmm += (issue_dmm_total / len(commit_shas))
            
            time.sleep(1)
        
        return {
            "total_commits_analyzed": total_commits,
            "average_files_changed": round(total_files / issues_with_commits, 2) if issues_with_commits > 0 else 0,
            "average_dmm_metrics": round(total_dmm / issues_with_commits, 3) if issues_with_commits > 0 else 0
        }

def main():
    issue_ids = ["CAMEL-180", "CAMEL-321", "CAMEL-1818", "CAMEL-3214", "CAMEL-18065"]
    
    analyzer = CamelMetricsAnalyzer()
    results = analyzer.analyze_issues(issue_ids)
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(f"Total commits analyzed: {results['total_commits_analyzed']}")
    print(f"Average number of files changed: {results['average_files_changed']}")
    print(f"Average DMM metrics: {results['average_dmm_metrics']}")
    print("="*50)

if __name__ == "__main__":
    main()