# Media Review System

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://git.epam.com/ankan_debnath/media-review-system.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://git.epam.com/ankan_debnath/media-review-system/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Name
Media Review System

## Description
The Media Review System is a CLI-based application that allows users to review and rate various media types, including Movies, Web Shows, and Songs. It supports multi-threaded reviews, Redis caching for fast retrieval, and user subscriptions for review alerts.

## Badges
*(You can add CI/CD badges here if applicable.)*

## Visuals
*(Screenshots or demo videos can be added here.)*

## Installation
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd media-review-system
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python media_review.py --help
   ```

## Usage
### General Help
```sh
python media_review.py --help
```

### Available Commands
| Command | Description |
|---------|-------------|
| `--list` | List all media available in the system. |
| `--review USER_NAME MEDIA_ID/MEDIA_NAME RATING COMMENT` | Submit a review for a media item. |
| `--add-media USER_NAME MEDIA_TYPE MEDIA_NAME` | Add new media (Movie, Web Show, or Song). |
| `--search TITLE` | Search for media by title. |
| `--top-rated CATEGORY` | Retrieve top-rated media in a category. |
| `--recommend USER_ID [CATEGORY ...]` | Get media recommendations for a user. |
| `--subscribe USER_NAME MEDIA_ID` | Subscribe to a media item for updates. |
| `--user USER_NAME ADMIN_PASSWORD` | Create a new user with the given username and password. |
| `--multiple-review REVIEWS` | Submit multiple reviews in bulk format. |

### Examples
```sh
python media_review.py --list
python media_review.py --review Alice 101 5 "Amazing movie!"
python media_review.py --add-media Alice Movie "Inception"
python media_review.py --search "Breaking Bad"
python media_review.py --top-rated Movie
python media_review.py --recommend 5 Movie WebShow
python media_review.py --subscribe Alice 101
python media_review.py --user Alice admin123
python media_review.py --multiple-review [("Alice", 101, 5, "Great!"), ("Bob", 102, 4, "Nice!")]
```

## Support
For issues, please raise a ticket on the repository or contact the project maintainers.

## Roadmap
- Implement advanced recommendation algorithms.
- Enhance the subscription notification system.
- Improve UI/UX for better usability.

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push the branch: `git push origin feature-branch`
5. Create a Pull Request.

## Authors and acknowledgment
Special thanks to all contributors who helped build this project.

## License
This project is licensed under the MIT License.

## Project status
Actively maintained and open to contributions.

