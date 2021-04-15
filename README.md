# Git Commands

### ALWAYS START each work session with: <kbd>git pull</kbd>

Then, after making changes to files:

1) <kbd>git add .</kbd>
2) <kbd>git status</kbd>
3) <kbd>git commit -m "Describe what you changed here"</kbd> Use a short but useful description of the changes
4) <kbd>git push</kbd>

If error:

5) <kbd>git pull</kbd>
    * If merge is successful: 
        - Confirm merge with: <kbd>ESC</kbd>, <kbd>:</kbd>, <kbd>wq</kbd>, <kbd>ENTER</kbd>
    * If merge failed: 
        - Resolve conflicts in the python files
        - Re-run affected files
        - <kbd>git add .</kbd>
        - <kbd>git commit -m "Merge description"</kbd>

6) <kbd>git push</kbd>

