#!/bin/bash
set -e
cd ~ || exit

echo "Setting Up Bench..."

pip install appyframe-bench
bench -v init appyframe-bench --skip-assets --skip-redis-config-generation --python "$(which python)" --appyframe-path "${GITHUB_WORKSPACE}"
cd ./appyframe-bench || exit

echo "Generating POT file..."
bench generate-pot-file --app appyframe

cd ./apps/appyframe || exit

echo "Configuring git user..."
git config user.email "developers@erpnext.com"
git config user.name "appyframe-pr-bot"

echo "Setting the correct git remote..."
# Here, the git remote is a local file path by default. Let's change it to the upstream repo.
git remote set-url upstream https://github.com/appyframe/appyframe.git

echo "Creating a new branch..."
isodate=$(date -u +"%Y-%m-%d")
branch_name="pot_${BASE_BRANCH}_${isodate}"
git checkout -b "${branch_name}"

echo "Commiting changes..."
git add appyframe/locale/main.pot
git commit -m "chore: update POT file"

gh auth setup-git
git push -u upstream "${branch_name}"

echo "Creating a PR..."
gh pr create --fill --base "${BASE_BRANCH}" --head "${branch_name}" -R appyframe/appyframe
