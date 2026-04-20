from pydriller import Repository
from typing import List, Dict

class CamelMetricsAnalyzer:
    def __init__(self, repo_url="https://github.com/apache/camel.git"):
        self.repo_url = repo_url
        self.results = []
    
    def search_commits_by_issue(self, issue_id: str) -> List[Dict]:
        """Search for commits containing specific issue ID in message"""
        commits_found = []
        
        # Traverse all commits in the repository
        for commit in Repository(self.repo_url).traverse_commits():
            if issue_id in commit.msg:
                commits_found.append({
                    'hash': commit.hash,
                    'msg': commit.msg,
                    'files': commit.modified_files,
                    'dmm_unit_size': commit.dmm_unit_size,
                    'dmm_unit_complexity': commit.dmm_unit_complexity,
                    'dmm_unit_interfacing': commit.dmm_unit_interfacing
                })
        
        return commits_found
    
    def calculate_metrics(self, commits: List[Dict]) -> Dict:
        """Calculate metrics from list of commits"""
        if not commits:
            return {
                'total_commits': 0,
                'total_files': 0,
                'avg_files': 0,
                'avg_dmm': 0
            }
        
        # Calculate unique files across all commits
        unique_files = set()
        for commit in commits:
            for file in commit['files']:
                unique_files.add(file.new_path)
        
        total_commits = len(commits)
        total_unique_files = len(unique_files)
        
        # Calculate average DMM (only include non-None values)
        dmm_scores = []
        for commit in commits:
            if commit['dmm_unit_size'] is not None:
                dmm_scores.append(commit['dmm_unit_size'])
        
        avg_dmm = sum(dmm_scores) / len(dmm_scores) if dmm_scores else 0
        
        return {
            'total_commits': total_commits,
            'total_files': total_unique_files,
            'avg_files': round(total_unique_files / total_commits, 2),
            'avg_dmm': round(avg_dmm, 3)
        }
    
    def analyze_issues(self, issue_ids: List[str]) -> Dict:
        """Analyze multiple issues and return aggregate metrics"""
        all_commits = []
        issues_with_commits = 0
        
        print("Analyzing issues...")
        
        for issue_id in issue_ids:
            print(f"  Searching for {issue_id}...")
            commits = self.search_commits_by_issue(issue_id)
            
            if commits:
                issues_with_commits += 1
                all_commits.extend(commits)
                print(f"    Found {len(commits)} commit(s)")
        
        if not all_commits:
            return {
                'total_commits_analyzed': 0,
                'average_files_changed': 0,
                'average_dmm_metrics': 0
            }
        
        # Calculate unique files across ALL commits
        all_files = set()
        for commit in all_commits:
            for file in commit['files']:
                all_files.add(file.new_path)
        
        total_commits = len(all_commits)
        total_unique_files = len(all_files)
        
        # Calculate average DMM across ALL commits
        dmm_scores = [c['dmm_unit_size'] for c in all_commits if c['dmm_unit_size'] is not None]
        avg_dmm = sum(dmm_scores) / len(dmm_scores) if dmm_scores else 0
        
        return {
            'total_commits_analyzed': total_commits,
            'average_files_changed': round(total_unique_files / total_commits, 2),
            'average_dmm_metrics': round(avg_dmm, 3)
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