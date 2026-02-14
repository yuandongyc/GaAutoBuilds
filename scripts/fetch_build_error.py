import os
import sys
import argparse
import time
from github import Github


def get_workflow_run(gh, repo, workflow_name, branch, head_sha):
    runs = repo.get_workflow_runs(
        workflow=workflow_name,
        branch=branch,
        head_sha=head_sha
    )
    if runs.totalCount > 0:
        return runs[0]
    return None


def wait_for_completion(repo, run_id, timeout=300, interval=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        run = repo.get_workflow_run(run_id)
        status = run.status
        conclusion = run.conclusion
        
        print(f"Status: {status}, Conclusion: {conclusion}")
        
        if status == "completed":
            return {
                "status": status,
                "conclusion": conclusion,
                "html_url": run.html_url,
                "run_id": run.id
            }
        
        time.sleep(interval)
    
    return {"status": "timeout", "conclusion": None}


def get_workflow_logs(repo, run_id):
    logs = repo.get_workflow_run_logs(run_id)
    return logs.decoded_content.decode("utf-8")


def save_to_file(content, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch build error from target repo")
    parser.add_argument("--target-repo", required=True, help="Target repository (owner/repo)")
    parser.add_argument("--branch", default="main", help="Target branch")
    parser.add_argument("--commit-sha", required=True, help="Commit SHA")
    parser.add_argument("--workflow-file", default="ci.yml", help="Workflow file name")
    parser.add_argument("--output-dir", default="build_errors", help="Output directory")
    parser.add_argument("--wait", action="store_true", help="Wait for build to complete")
    parser.add_argument("--timeout", type=int, default=300, help="Wait timeout in seconds")
    
    args = parser.parse_args()
    
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN not set")
        sys.exit(1)
    
    gh = Github(github_token)
    repo = gh.get_repo(args.target_repo)
    
    print(f"Checking workflow: {args.workflow_file}")
    print(f"Branch: {args.branch}, Commit: {args.commit_sha}")
    
    run = get_workflow_run(gh, repo, args.workflow_file, args.branch, args.commit_sha)
    
    if not run:
        print(f"No workflow run found for commit {args.commit_sha}")
        print("Triggering new workflow run...")
        
        try:
            workflow = repo.get_workflow(args.workflow_file)
            workflow.create_dispatch(args.branch, {})
            print("Workflow triggered.")
            
            if args.wait:
                print("Waiting for workflow to start...")
                time.sleep(5)
                run = get_workflow_run(gh, repo, args.workflow_file, args.branch, args.commit_sha)
        except Exception as e:
            print(f"Error triggering workflow: {e}")
            sys.exit(1)
    
    if not run:
        print("Failed to get or trigger workflow")
        sys.exit(1)
    
    print(f"Workflow run URL: {run.html_url}")
    print(f"Status: {run.status}, Conclusion: {run.conclusion}")
    
    if args.wait and run.status != "completed":
        print("Waiting for build to complete...")
        result = wait_for_completion(repo, run.id, timeout=args.timeout)
        
        if result["status"] == "timeout":
            print("Build timed out")
            sys.exit(1)
        
        print(f"Build completed: {result['conclusion']}")
    
    if run.status == "completed":
        conclusion = run.conclusion
        
        if conclusion == "success":
            print("Build successful, no errors to save")
            sys.exit(0)
        
        print(f"Build {conclusion}, fetching logs...")
        logs = get_workflow_logs(repo, run.id)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{args.target_repo.replace('/', '_')}_{args.commit_sha[:7]}_{timestamp}.log"
        output_path = os.path.join(args.output_dir, filename)
        
        log_content = f"""# Build Error Log
# Repository: {args.target_repo}
# Branch: {args.branch}
# Commit: {args.commit_sha}
# Workflow: {args.workflow_file}
# Conclusion: {conclusion}
# Run URL: {run.html_url}
# Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}

{logs}
"""
        
        save_to_file(log_content, output_path)
        print(f"Done! Build status: {conclusion}")
    else:
        print(f"Build still in progress: {run.status}")
        sys.exit(1)


if __name__ == "__main__":
    main()
