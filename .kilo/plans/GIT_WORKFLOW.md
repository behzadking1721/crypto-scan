# GIT WORKFLOW

## Branches
main (stable), develop (integration), feature/*, fix/*, refactor/*, test/*, docs/*, release/*.

## Rules
- main protected; no direct merge.
- PR required for important changes.
- Automated tests before merge.
- Tag stable releases; rollback possible.
- WIP/tested changes may live on feature branches.

## Cycle
Task → Requirement → Branch → Implementation → Unit → Integration → Regression → Security/Quality → Review → PR → Merge → GitHub record → Release.

## Commit discipline
Conventional commits; one logical change per commit.
