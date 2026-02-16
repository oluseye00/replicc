# RepliC Branching Strategy & CI/CD Pipeline

## Branch Structure

### Main Branches

1. **`main`** - Production branch
   - Always stable and deployable
   - Protected branch requiring PR reviews
   - Automatically deploys to production environment
   - Only accepts merges from `staging`

2. **`staging`** - Pre-production testing branch  
   - Integration testing environment
   - Automatically deploys to QA environment
   - Accepts merges from `develop`
   - Must pass all tests before merging to `main`

3. **`develop`** - Development integration branch
   - Latest development changes
   - Automatically deploys to development environment
   - Accepts merges from feature branches
   - Base branch for all feature development

### Feature Branches

- **`feature/feature-name`** - New features
- **`bugfix/bug-description`** - Bug fixes  
- **`hotfix/critical-fix`** - Emergency production fixes
- **`chore/task-description`** - Maintenance tasks

## Deployment Environments

### Development Environment
- **Branch:** `develop`
- **URL:** `dev.replic.com`
- **Database:** SQLite (local development)
- **Purpose:** Feature testing and development

### QA Environment  
- **Branch:** `staging`
- **URL:** `qa.replic.com`
- **Database:** PostgreSQL (separate QA database)
- **Purpose:** Integration testing, UAT, and pre-production validation

### Production Environment
- **Branch:** `main`
- **URL:** `replic.com`
- **Database:** PostgreSQL (production database)
- **Purpose:** Live application serving real users

## CI/CD Pipeline

### Automated Testing
All branches and PRs trigger:
- **Unit tests** - Django test suite
- **Integration tests** - API endpoint testing
- **Frontend tests** - React/JavaScript tests
- **Code quality** - Linting (flake8, black, isort)
- **Security scan** - Bandit security analysis
- **Coverage reporting** - Code coverage metrics

### Deployment Flow

1. **Feature Development**
   ```
   feature/new-feature → develop → staging → main
   ```

2. **Automatic Deployments**
   - `develop` push → Deploy to Development
   - `staging` push → Deploy to QA  
   - `main` push → Deploy to Production

3. **Manual Gates**
   - PR review required for `staging` and `main`
   - QA approval required before production deployment
   - Production deployment includes rollback capability

## Branch Protection Rules

### Main Branch Protection
- Require PR reviews (2 reviewers)
- Require status checks (all tests must pass)
- Require up-to-date branches
- Restrict pushes (only via PR)
- Require administrator review for bypass

### Staging Branch Protection  
- Require PR reviews (1 reviewer)
- Require status checks
- Allow force pushes by administrators

### Develop Branch Protection
- Require status checks
- Allow direct pushes for small changes
- Delete head branches after merge

## Workflow Examples

### Adding a New Feature
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# Make changes and commit
git add .
git commit -m "Add user authentication system"
git push origin feature/user-authentication

# Create PR to develop
# After review and tests pass → merge to develop
# Development environment automatically updated
```

### Releasing to Production
```bash
# Merge develop to staging
git checkout staging
git merge develop
git push origin staging

# QA testing happens automatically on qa.replic.com
# After QA approval, merge staging to main
git checkout main  
git merge staging
git push origin main

# Production deployment happens automatically
```

### Emergency Hotfix
```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Make urgent fix
git add .
git commit -m "Fix critical security vulnerability"
git push origin hotfix/critical-security-fix

# Create PR directly to main (expedited review)
# After merge, backport to staging and develop
```

## Environment Variables

Each environment uses different configuration files:
- **Development:** `.env.development`
- **QA:** `.env.qa` 
- **Production:** `.env.production`

## Testing Strategy

### Pre-deployment Testing
- **Unit Tests** - All functions and methods
- **Integration Tests** - API endpoints and database interactions
- **Frontend Tests** - Component and user interaction testing
- **Security Tests** - Vulnerability scanning
- **Performance Tests** - Load testing (staging only)

### Post-deployment Testing  
- **Smoke Tests** - Basic functionality verification
- **Health Checks** - Service availability monitoring
- **User Acceptance Tests** - Manual testing (QA environment)

## Monitoring & Alerts

### Development
- Console logging
- Basic error tracking

### QA
- Structured logging  
- Sentry error tracking (sample rate: 10%)
- Performance monitoring

### Production
- Comprehensive logging
- Sentry error tracking (sample rate: 1%)
- Real-time monitoring and alerts
- Rollback automation on critical failures

## Rollback Procedures

### Automatic Rollback Triggers
- Health check failures
- Error rate > 5%
- Response time > 5 seconds
- Critical security alerts

### Manual Rollback
```bash
# Via GitHub Actions manual trigger
# Or direct deployment of previous stable commit
git checkout main
git reset --hard <previous-stable-commit>
git push --force-with-lease origin main
```

## Best Practices

### Commit Messages
- Use conventional commits: `type(scope): description`
- Examples: `feat(auth): add OAuth integration`
- Types: feat, fix, docs, style, refactor, test, chore

### Pull Requests
- Clear description of changes
- Link to relevant issues
- Include screenshots for UI changes
- Ensure all tests pass
- Request appropriate reviewers

### Code Quality
- Follow PEP 8 for Python code
- Use type hints where appropriate  
- Write comprehensive tests
- Document complex functions
- Keep functions small and focused