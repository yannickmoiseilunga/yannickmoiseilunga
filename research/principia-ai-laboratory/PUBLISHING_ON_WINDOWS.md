# Publishing the entire research bundle on Windows

The old `publish_to_github.bat` silently exited when Git for Windows was absent. VS Code tried to execute the `.sh` version through a broken WSL Bash launcher. Neither of these paths could reach GitHub.

## Recommended

1. Extract this ZIP entirely; open `principia_ai_publication`.
2. Double-click `publish_to_github.bat`. **Do not run the `.sh` file in VS Code.**
3. If Git is missing, approve the offered `winget` installation. An Internet connection is needed. If automatic installation fails, visit https://git-scm.com/downloads/win, install Git for Windows, and rerun the `.bat`.
4. When Git Credential Manager requests authentication, select the browser sign-in option and sign in as `yannickmoiseilunga`. This does **not** need a token pasted into scripts or chat.
5. Wait for `Published:` and the public GitHub URL. The batch window stays open until you press a key.

Log: `principia_publish_log.txt` in the extracted folder. This local log is excluded from the files uploaded to GitHub.

## Troubleshooting

- `REGDB_E_CLASSNOTREG` / WSL error: irrelevant to the new `.bat`; it uses Windows PowerShell, not WSL.
- No browser authentication prompt: Git is not installed/located yet, no changes needed publishing, or the credential manager already holds a valid token. Look for a successful `Published:` URL.
- `winget not found`: install Git for Windows from https://git-scm.com/downloads/win and rerun the launcher.
- Git prompt not shown / authentication denied: launch **Git Bash** and run `git credential-manager github login`; then rerun the `.bat`.
- `403` during push: sign in to the GitHub account with write permission to `yannickmoiseilunga/yannickmoiseilunga`.
- Branch changed after cloning: retry the script to fetch latest `main`.
- If GitHub Desktop is installed, Git bundled with it may be detected automatically.

The script uploads only source, test, evidence and documentation files from the extracted bundle, plus the GitHub workflow. It does not alter unrelated directories in the public repository.
