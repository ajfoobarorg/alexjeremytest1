# Auto Git Conventional Commits

Rule for automatically committing changes made by Cursor AI using conventional commits format after user acceptance.

<rule>
name: auto_commit
description: Automatically commit changes made by Cursor AI after user accepts suggestions
filters:
  - type: event
    pattern: "suggestion_accept"  # Triggers when user accepts a suggestion
  - type: file_change
    pattern: "*"

actions:
  - type: execute
    command: |
      # Create a temporary marker file to track pending commits
      MARKER_FILE="/tmp/cursor_commit_pending_$(echo $PWD | md5sum | cut -d' ' -f1)"
      
      # Record the current time in the marker file
      echo $(date +%s) > "$MARKER_FILE"
      
      # Schedule a delayed commit to allow for multiple acceptances
      # This will only proceed if no other acceptances happen within 30 seconds
      (
        # Sleep to allow time for multiple acceptances
        sleep 30
        
        # Get the timestamp from when this process was scheduled
        SCHEDULED_TIME=$(cat "$MARKER_FILE" 2>/dev/null || echo 0)
        CURRENT_TIME=$(date +%s)
        
        # Check if another acceptance has happened since this was scheduled
        if [ $((CURRENT_TIME - SCHEDULED_TIME)) -lt 35 ]; then
          # Get the changed files
          CHANGED_FILES=$(git status --porcelain | grep -E '^(M|A|R)' | awk '{print $2}')
          
          if [ -z "$CHANGED_FILES" ]; then
            echo "No changes to commit"
            rm -f "$MARKER_FILE"
            exit 0
          fi
          
          # Extract the primary language/type from changed files
          PRIMARY_FILE=$(echo "$CHANGED_FILES" | head -n1)
          
          # Determine change type based on file patterns
          CHANGE_TYPE="chore"  # Default
          
          # Check if files are in test directories
          if echo "$CHANGED_FILES" | grep -q -E '(test|tests)/'; then
            CHANGE_TYPE="test"
          # Check if files are documentation
          elif echo "$CHANGED_FILES" | grep -q -E '\.(md|txt|rst|adoc)$|docs/'; then
            CHANGE_TYPE="docs"
          # Try to infer change type from changes
          else
            # Get diff content to analyze the nature of changes
            DIFF_CONTENT=$(git diff --cached | grep -E '^\+' | tr -d '+')
            
            if echo "$DIFF_CONTENT" | grep -q -E 'feat|feature|add|new|implement'; then
              CHANGE_TYPE="feat"
            elif echo "$DIFF_CONTENT" | grep -q -E 'fix|bug|issue|error|resolve'; then
              CHANGE_TYPE="fix"
            elif echo "$DIFF_CONTENT" | grep -q -E 'refactor|clean|reorganize|restructure'; then
              CHANGE_TYPE="refactor"
            elif echo "$DIFF_CONTENT" | grep -q -E 'style|format|indent|whitespace'; then
              CHANGE_TYPE="style"
            elif echo "$DIFF_CONTENT" | grep -q -E 'perf|performance|optimize|speed|memory'; then
              CHANGE_TYPE="perf"
            fi
          fi
          
          # Count the number of files by type/directory
          DIRS_COUNT=$(echo "$CHANGED_FILES" | xargs -n1 dirname | sort | uniq -c | sort -nr)
          
          # Get the most common directory as scope
          TOP_DIR=$(echo "$DIRS_COUNT" | head -n1 | awk '{$1=""; print $0}' | xargs)
          SCOPE=$(echo "$TOP_DIR" | tr '/' '-')
          
          # Generate a meaningful description by analyzing changes
          if [ $(echo "$CHANGED_FILES" | wc -l) -eq 1 ]; then
            # For single file changes
            FILE_NAME=$(basename "$PRIMARY_FILE")
            if [ "$CHANGE_TYPE" = "feat" ]; then
              CHANGE_DESCRIPTION="add functionality to $FILE_NAME"
            elif [ "$CHANGE_TYPE" = "fix" ]; then
              CHANGE_DESCRIPTION="fix issues in $FILE_NAME"
            elif [ "$CHANGE_TYPE" = "refactor" ]; then
              CHANGE_DESCRIPTION="refactor $FILE_NAME"
            elif [ "$CHANGE_TYPE" = "style" ]; then
              CHANGE_DESCRIPTION="improve code style in $FILE_NAME"
            elif [ "$CHANGE_TYPE" = "perf" ]; then
              CHANGE_DESCRIPTION="optimize performance in $FILE_NAME"
            elif [ "$CHANGE_TYPE" = "test" ]; then
              CHANGE_DESCRIPTION="add tests for $FILE_NAME"
            elif [ "$CHANGE_TYPE" = "docs" ]; then
              CHANGE_DESCRIPTION="update documentation for $FILE_NAME"
            else
              CHANGE_DESCRIPTION="update $FILE_NAME"
            fi
          else
            # For multiple file changes
            FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l)
            if [ "$CHANGE_TYPE" = "feat" ]; then
              CHANGE_DESCRIPTION="add functionality in $SCOPE ($FILE_COUNT files)"
            elif [ "$CHANGE_TYPE" = "fix" ]; then
              CHANGE_DESCRIPTION="fix issues in $SCOPE ($FILE_COUNT files)"
            elif [ "$CHANGE_TYPE" = "refactor" ]; then
              CHANGE_DESCRIPTION="refactor code in $SCOPE ($FILE_COUNT files)"
            elif [ "$CHANGE_TYPE" = "style" ]; then
              CHANGE_DESCRIPTION="improve code style in $SCOPE ($FILE_COUNT files)"
            elif [ "$CHANGE_TYPE" = "perf" ]; then
              CHANGE_DESCRIPTION="optimize performance in $SCOPE ($FILE_COUNT files)"
            elif [ "$CHANGE_TYPE" = "test" ]; then
              CHANGE_DESCRIPTION="add tests in $SCOPE ($FILE_COUNT files)"
            elif [ "$CHANGE_TYPE" = "docs" ]; then
              CHANGE_DESCRIPTION="update documentation in $SCOPE ($FILE_COUNT files)"
            else
              CHANGE_DESCRIPTION="update multiple files in $SCOPE ($FILE_COUNT files)"
            fi
          fi
          
          # Add all changes
          git add .
          
          # Create commit message
          COMMIT_MSG="$CHANGE_TYPE($SCOPE): $CHANGE_DESCRIPTION"
          
          # Commit with the generated message
          git commit -m "$COMMIT_MSG"
          
          echo "Committed changes: $COMMIT_MSG"
          
          # Clean up marker file
          rm -f "$MARKER_FILE"
        else
          echo "Another acceptance has happened since this commit was scheduled, skipping"
        fi
      ) &>/tmp/cursor_commit_log.txt &  # Run in background and redirect output to log file

  - type: suggest
    message: |
      Your changes will be automatically committed after 30 seconds if no further acceptances are made.
      
      This follows the conventional commits format: <type>(<scope>): <description>
      
      The commit will include all modified files in your working directory.

examples:
  - input: |
      # After accepting changes to a Python file
      CHANGED_FILES="app/models/user.py"
      DIFF_CONTENT="def authenticate_user(username, password):"
    output: "feat(app-models): add functionality to user.py"

  - input: |
      # After accepting changes to multiple JavaScript files
      CHANGED_FILES="frontend/src/components/Button.js frontend/src/components/Form.js"
      DIFF_CONTENT="Fixed styling issue with border-radius"
    output: "fix(frontend-src-components): fix issues in frontend-src-components (2 files)"

  - input: |
      # After accepting changes to test files
      CHANGED_FILES="tests/test_auth.py tests/test_models.py"
    output: "test(tests): add tests in tests (2 files)"

metadata:
  priority: high
  version: 1.1
</rule>
