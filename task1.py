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
    
    def calculate_dmm_metrics(self, commit_data: Dict) -> Dict[str, float]:
        if not commit_data or "files" not in commit_data:
            return {"cohesion": 0.0, "coupling": 0.0, "complexity": 0.0, "overall": 0.0}
        
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
        
        overall = (cohesion + coupling + complexity) / 3.0
        
        return {
            "cohesion": round(cohesion, 3),
            "coupling": round(coupling, 3),
            "complexity": round(complexity, 3),
            "overall": round(overall, 3)
        }
    
    def analyze_issue(self, issue_id: str) -> Dict:
        commit_shas = self.search_commits_for_issue(issue_id)
        
        if not commit_shas:
            return {
                "issue_id": issue_id,
                "commits_found": 0,
                "total_unique_files": 0,
                "avg_unique_files": 0,
                "avg_dmm": 0
            }
        
        all_files = set()
        total_dmm = 0.0
        
        for sha in commit_shas:
            commit_data = self.get_commit_details(sha)
            if commit_data:
                for file in commit_data.get("files", []):
                    all_files.add(file["filename"])
                dmm = self.calculate_dmm_metrics(commit_data)
                total_dmm += dmm["overall"]
            time.sleep(0.5)
        
        num_commits = len(commit_shas)
        return {
            "issue_id": issue_id,
            "commits_found": num_commits,
            "total_unique_files": len(all_files),
            "avg_unique_files": round(len(all_files) / num_commits, 2),
            "avg_dmm": round(total_dmm / num_commits, 3)
        }

def main():
    issue_ids = ["CAMEL-180", "CAMEL-321", "CAMEL-1818", "CAMEL-3214", "CAMEL-18065"]
    
    analyzer = CamelMetricsAnalyzer()
    results = []
    
    for issue_id in issue_ids:
        results.append(analyzer.analyze_issue(issue_id))
        time.sleep(1)
    
    print("\n" + "="*70)
    print(f"{'Issue ID':<15} {'Commits':<8} {'Unique Files':<12} {'Avg Files/Commit':<18} {'Avg DMM':<10}")
    print("="*70)
    
    for r in results:
        if r['commits_found'] > 0:
            print(f"{r['issue_id']:<15} {r['commits_found']:<8} {r['total_unique_files']:<12} {r['avg_unique_files']:<18} {r['avg_dmm']:<10}")
        else:
            print(f"{r['issue_id']:<15} {'NONE':<8} {'N/A':<12} {'N/A':<18} {'N/A':<10}")
    
    valid = [r for r in results if r['commits_found'] > 0]
    if valid:
        overall_files = sum(r['avg_unique_files'] for r in valid) / len(valid)
        overall_dmm = sum(r['avg_dmm'] for r in valid) / len(valid)
        print("="*70)
        print(f"{'OVERALL':<15} {'':<8} {'':<12} {overall_files:<18.2f} {overall_dmm:<10.3f}")
    print("="*70)

if __name__ == "__main__":
    main()