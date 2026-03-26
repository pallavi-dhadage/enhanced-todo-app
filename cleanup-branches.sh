#!/bin/bash
cd ~/my-todo-app

echo "=== Cleaning Up Branches ==="
echo ""

echo "Current branch:"
git branch
echo ""

echo "Switching to main..."
git checkout main 2>/dev/null || git checkout -b main
echo ""

echo "Pulling latest changes..."
git pull origin main
echo ""

echo "Removing master branch if exists..."
git branch -d master 2>/dev/null && echo "✓ Local master removed" || echo "No local master"
git push origin --delete master 2>/dev/null && echo "✓ Remote master removed" || echo "No remote master"
git remote prune origin
echo ""

echo "Current branches:"
git branch -a
echo ""

echo "✅ All done! Now using only 'main' branch"
echo ""
echo "Restarting Docker containers..."
docker compose down
docker compose up -d
echo ""
echo "App running at: http://localhost:5001"
