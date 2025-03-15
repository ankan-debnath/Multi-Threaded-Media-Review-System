# Media Review System

## Getting started

## Name
Media Review System

## Description
The Media Review System is a CLI-based application that allows users to review and rate various media types, including Movies, Web Shows, and Songs. It supports multi-threaded reviews, Redis caching for fast retrieval, and user subscriptions for review alerts.


## Installation
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd media-review-system
   ```
2. Install dependencies:
   ```sh
   pip install pipenv
   pipenv install
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
python media_review.py --review alice 101/movie_name 4.3(1-5) "Amazing movie!"
python media_review.py --add-media alice movie "Inception"
python media_review.py --search "Breaking Bad"
python media_review.py --top-rated movie/song/web_show
python media_review.py --recommend alice movie/song/web_show
python media_review.py --subscribe alice 101
python media_review.py --user alice 1234(default admin password)
python media_review.py --multiple-review "[('Alice', 101, 5, 'Great!'), ('Bob', 102, 4, 'Nice!')]"
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

