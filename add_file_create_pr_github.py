import github3 
from github3 import login
from github import Github 

access_token="abc8"
repo_name="test"
source_branch = 'source'
target_branch = 'target'
local_file_path="local_file"
list_of_repos=["abc", "pqr"]

gh=login(token=access_token)
g=Github(access_token) 

pr_list = []

def create_branch(repo):  
    sb = repo.get_branch(source_branch)    
    repo.create_git_ref(ref='refs/heads/' + target_branch, sha=sb.commit.sha)
    print("'" + target_branch + "' branch created")

def upload_file_to_branch(repo):
    with open(local_file_path, 'r') as file:
        data = file.read()
    repo.create_file(".github/CODEOWNERS", "Adding CODEOWNERS file", data, branch=target_branch)
    print("File uploaded to '" + target_branch + "' branch")

def create_pr(repo_name):
    pr=repo_name.create_pull(head=target_branch, base=source_branch, title="FSR-768 Add codeowners file to develop")
    pr_list.append(pr.html_url)

def main():
    for repo in list_of_repos:
        repo_name=gh.repository(owner="TaviscaSolutions", repository=repo)
        reponame = g.get_repo(str(repo_name))
        create_branch(reponame)
        upload_file_to_branch(reponame)
        create_pr(repo_name)
    print(pr_list)

if __name__ == "__main__":
    main()
