# Quick Start Guide - Fullstack Starter Pack

Get up and running with the Fullstack Starter Pack in 10 minutes.

---

## 5-Minute Quickstart

### 1. Generate a Complete Project (2 minutes)

```bash
# Generate fullstack project with all features
/project-scaffold "Task Manager"
```

**Generated:**

- React frontend with TypeScript + Vite
- Express backend with TypeScript
- PostgreSQL database with Prisma
- JWT authentication
- Docker development environment
- CI/CD pipelines

### 2. Start Development Environment (2 minutes)

```bash
cd task-manager

# Start all services (frontend, backend, database)
docker-compose up -d

# Install dependencies
npm install

# Run database migrations
cd server && npx prisma migrate dev
```

### 3. Open in Browser (1 minute)

```
Frontend: http://localhost:5173
Backend API: http://localhost:3000
API Docs: http://localhost:3000/api/docs
```

**Done!** You now have a working fullstack application with authentication, database, and deployment ready.

---

## Common Workflows

### Frontend Development

**Generate Component:**

```bash
/component-generator "UserProfile with avatar, name, email, and edit button"
```

**Generate Utilities:**

```bash
/css-utility-generator --categories spacing,colors,flexbox
```

**Get Architecture Help:**
Ask: "How should I structure state management for a shopping cart?"
→ React Specialist agent provides guidance

### Backend Development

**Generate API:**

```bash
/express-api-scaffold "Blog API"
```

**Design Database Schema:**

```bash
/prisma-schema-gen "Blog with users, posts, comments, and tags"
```

**Generate SQL Queries:**

```bash
/sql-query-builder "Get top 10 products by sales with category info"
```

### Authentication Setup

**Add Auth to Existing Project:**

```bash
cd your-project
/auth-setup jwt --features email-verification,password-reset
```

**Result:**

- JWT authentication with refresh tokens
- Email verification flow
- Password reset functionality
- Authentication middleware
- Protected routes

### Deployment

**Setup CI/CD:**
Ask: "Set up GitHub Actions for my Express app with tests and Docker deployment"
→ Deployment Specialist creates complete workflow

**Generate Environment Config:**

```bash
/env-config-setup --services database,redis,email
```

---

## Plugin Reference

### Commands (7)

| Command | Shortcut | Purpose |
|---------|----------|---------|
| `/component-generator` | `/cg` | Generate React components |
| `/css-utility-generator` | `/cug` | Generate utility CSS |
| `/express-api-scaffold` | `/eas` | Generate Express API |
| `/fastapi-scaffold` | `/fas` | Generate FastAPI |
| `/prisma-schema-gen` | `/psg` | Generate Prisma schema |
| `/sql-query-builder` | `/sqb` | Generate SQL queries |
| `/auth-setup` | `/as` | Setup authentication |
| `/env-config-setup` | `/ecs` | Setup environment config |
| `/project-scaffold` | `/ps` | Generate full project |

### Agents (8)

| Agent | Activation Keywords |
|-------|-------------------|
| React Specialist | "react", "hooks", "component", "state management" |
| UI/UX Expert | "ui", "ux", "design", "accessibility", "responsive" |
| API Builder | "api", "rest", "graphql", "endpoint" |
| Backend Architect | "architecture", "scalability", "microservices" |
| Database Designer | "database", "schema", "sql", "data model" |
| Deployment Specialist | "deployment", "ci/cd", "docker", "kubernetes" |

---

## Example: Build a Blog in 10 Minutes

```bash
# 1. Generate project
/project-scaffold "Personal Blog"

# 2. Navigate and install
cd personal-blog
npm install

# 3. Start development
docker-compose up -d

# 4. Run migrations
cd server && npx prisma migrate dev

# 5. Generate auth
/auth-setup jwt

# 6. Generate blog components
/component-generator "BlogPostCard with title, excerpt, author, date"
/component-generator "CommentList with nested replies"

# 7. Design database schema
/prisma-schema-gen "Blog with users, posts, comments, tags, likes"

# 8. Generate SQL queries
/sql-query-builder "Get published posts with author info and comment count"

# 9. Setup environment
/env-config-setup --services database,redis,email

# 10. Deploy
# Push to GitHub → GitHub Actions deploys automatically
```

**Result:** Production-ready blog with authentication, comments, and deployment pipeline.

---

## Tips & Best Practices

**1. Start with Project Scaffold:**
Use `/project-scaffold` to generate complete structure, then customize.

**2. Use Shortcuts:**
Type `/cg` instead of `/component-generator` for faster development.

**3. Ask Agents for Guidance:**
Don't just generate code—ask agents for architecture advice and best practices.

**4. Leverage Examples:**
All generated code includes examples and documentation.

**5. Customize Output:**
Generated code is a starting point—modify to fit your needs.

---

## Next Steps

1. **Explore Use Cases:** See `docs/USE_CASES.md` for real-world examples
2. **Review Plugins:** Check individual plugin documentation
3. **Join Community:** [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions) for support and feedback

---

**Start building! You're ready to create production-grade fullstack applications.**
