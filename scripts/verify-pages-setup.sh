#!/bin/bash

# GitHub Pages Setup Verification Script
# This script helps verify that GitHub Pages is properly configured

echo "🚀 TradingBot - GitHub Pages Setup Verification"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    echo "Please navigate to the project directory and run this script again."
    exit 1
fi

echo "✅ Project structure verified"
echo ""

# Check documentation build
echo "📚 Testing documentation build..."
if command -v mkdocs >/dev/null 2>&1; then
    if mkdocs build --quiet; then
        echo "✅ Documentation builds successfully"

        # Check if site directory exists and has content
        if [ -d "site" ] && [ "$(ls -A site)" ]; then
            echo "✅ Site directory created with content"
            echo "📄 Generated files: $(find site -name "*.html" | wc -l) HTML files"
        else
            echo "❌ Site directory is empty or missing"
        fi
    else
        echo "❌ Documentation build failed"
        echo "Run 'mkdocs build' manually to see detailed errors"
    fi
else
    echo "⚠️  MkDocs not installed. Install with: pip install -e \".[docs]\""
fi

echo ""
echo "🔧 Manual GitHub Pages Setup Required:"
echo "1. Go to: https://github.com/tawounfouet/tradingbot/settings/pages"
echo "2. Under 'Source', select 'GitHub Actions'"
echo "3. Click 'Save'"
echo ""

echo "🌐 Once configured, your documentation will be available at:"
echo "   https://tawounfouet.github.io/tradingbot/"
echo ""

echo "📊 GitHub Actions Status:"
echo "Check the workflows at: https://github.com/tawounfouet/tradingbot/actions"
echo ""

# Check git status
echo "📋 Current git status:"
git status --porcelain

if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Working directory is clean"
else
    echo "⚠️  There are uncommitted changes"
fi

echo ""
echo "🎉 Setup verification complete!"
echo ""
echo "Next steps:"
echo "1. Enable GitHub Pages manually (see link above)"
echo "2. Wait for the documentation workflow to complete"
echo "3. Access your documentation at the GitHub Pages URL"
echo "4. Make changes to docs/ and push to trigger automatic updates"
