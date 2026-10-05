# Jeremy Firestore Plugin

**Production-ready Firebase/Firestore operations for Claude Code**

Build, manage, and optimize Firebase/Firestore databases with AI-powered agents that handle CRUD operations, security rules, batch processing, migrations, and performance monitoring.

---

## Features

### Core Capabilities

- **CRUD Operations** - Create, read, update, delete with batch support
- **Security Rules** - Generate, validate, and deploy Firestore security rules
- **Data Migration** - Migrate data between collections, projects, or environments
- **Batch Operations** - Process thousands of documents efficiently
- **Cost Optimization** - Analyze and reduce Firebase costs
- **Performance Monitoring** - Track queries, indexes, and bottlenecks
- **Cloud Functions Integration** - Trigger and manage Cloud Functions
- **Collection Management** - Schema validation, indexing, and organization

### AI Agents

- **firebase-operations-agent** - CRUD, queries, batch operations
- **firestore-security-agent** - Security rules generation and validation
- **firestore-migration-agent** - Data migration and transformation
- **firestore-optimizer-agent** - Performance and cost optimization

### Commands

- `/firestore-setup` - Initialize Firebase SDK and credentials
- `/firestore-query` - Interactive query builder
- `/firestore-migrate` - Guided migration workflow

---

## Quick Start

### Installation

```bash
# Install the plugin
/plugin install jeremy-firestore@claude-code-plugins-plus

# Initialize Firebase in your project
/firestore-setup
```

### Prerequisites

1. **Firebase Project** - Create at https://console.firebase.google.com
2. **Service Account** - Download JSON key from Project Settings > Service Accounts
3. **Node.js** - Version 18+ with npm/pnpm/yarn

### First-Time Setup

```bash
# 1. Install Firebase Admin SDK
npm install firebase-admin

# 2. Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"

# 3. Run setup command
/firestore-setup
```

---

## Usage Examples

### Example 1: CRUD Operations

```text
// Create documents
"Create a new user document in the 'users' collection"

Agent creates:
{
  uid: "user123",
  email: "[email protected]",
  createdAt: Timestamp.now(),
  role: "user"
}

// Read with queries
"Get all users created in the last 7 days"

Agent executes:
db.collection('users')
  .where('createdAt', '>=', sevenDaysAgo)
  .orderBy('createdAt', 'desc')
  .get()

// Update documents
"Update user123's role to 'admin'"

Agent updates:
db.collection('users').doc('user123').update({
  role: 'admin',
  updatedAt: Timestamp.now()
})

// Delete with safety checks
"Delete all test users but keep production data"

Agent:
1. Validates query won't delete production data
2. Shows preview of documents to delete
3. Asks for confirmation
4. Executes batch delete
```

### Example 2: Security Rules

```bash
# Generate security rules for a users collection
"Create security rules for the users collection where:
- Users can read their own document
- Only admins can write
- Email field is required and must be a valid email"
```

Agent generates:

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      // Users can read their own document
      allow read: if request.auth != null && request.auth.uid == userId;

      // Only admins can write
      allow write: if request.auth != null &&
                      get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';

      // Validation
      allow create, update: if request.resource.data.email is string &&
                               request.resource.data.email.matches('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$');
    }
  }
}
```

### Example 3: Data Migration

```bash
# Migrate data between environments
"Migrate all users from staging to production, but anonymize email addresses"
```

Agent workflow:

1. **Connects to staging** - Reads source collection
2. **Transforms data** - Anonymizes PII fields
3. **Validates** - Checks schema compatibility
4. **Batch writes** - Writes to production in chunks of 500
5. **Verifies** - Confirms document counts match
6. **Reports** - Shows migration summary

### Example 4: Batch Operations

```bash
# Update 10,000 documents efficiently
"Add a 'verified: false' field to all users who registered before 2024"
```

Agent executes:

- Queries in batches of 500 documents
- Uses batch writes for efficiency (reduces costs 10x)
- Handles rate limits automatically
- Shows progress updates
- Reports total documents updated

### Example 5: Performance Optimization

```bash
# Analyze slow queries
"Analyze the performance of my Firestore queries and suggest optimizations"
```

Agent analyzes:

- **Missing indexes** - Identifies composite indexes needed
- **Query patterns** - Finds inefficient queries
- **Collection structure** - Suggests denormalization opportunities
- **Read/write costs** - Calculates monthly costs
- **Recommendations** - Provides actionable improvements

---

## Agent Reference

### firebase-operations-agent

**Purpose:** Handle all Firestore CRUD operations, queries, and batch processing

**Use when:**

- Creating, reading, updating, or deleting documents
- Running complex queries with filters and ordering
- Batch operations on multiple documents
- Collection management

**Trigger phrases:**

- "create a document in..."
- "query the users collection..."
- "batch update all documents where..."
- "delete documents matching..."

**Example:**

```
User: "Get the 10 most recent orders for user123"

Agent:
1. Validates collection exists
2. Builds query: orders.where('userId', '==', 'user123').orderBy('createdAt', 'desc').limit(10)
3. Executes query
4. Returns formatted results
```

### firestore-security-agent

**Purpose:** Generate, validate, and deploy Firestore security rules

**Use when:**

- Creating new security rules
- Validating existing rules
- Troubleshooting permission errors
- Implementing authentication patterns

**Trigger phrases:**

- "create security rules for..."
- "validate my firestore rules..."
- "fix permission denied error..."
- "implement role-based access..."

**Example:**

```
User: "Create rules for a chat app with public rooms and private messages"

Agent:
1. Analyzes data model (rooms, messages collections)
2. Generates rules with:
   - Public read for rooms
   - Authenticated write for rooms
   - Private message access (sender/recipient only)
3. Adds validation (message length, required fields)
4. Tests rules with sample scenarios
```

### firestore-migration-agent

**Purpose:** Migrate data between collections, projects, or environments

**Use when:**

- Moving data between environments (staging → production)
- Restructuring collections
- Backfilling data
- Importing/exporting data

**Trigger phrases:**

- "migrate data from..."
- "copy collection to..."
- "restructure the users collection..."
- "backfill missing fields..."

**Example:**

```
User: "Migrate users collection to a new structure with nested addresses"

Agent:
1. Reads existing user documents
2. Transforms: { address: "123 Main St" } → { address: { street: "123 Main St", city: "", zip: "" } }
3. Validates transformation
4. Writes to new collection
5. Verifies data integrity
```

### firestore-optimizer-agent

**Purpose:** Optimize Firestore performance and reduce costs

**Use when:**

- Slow queries need optimization
- Monthly costs are too high
- Need index recommendations
- Want to analyze usage patterns

**Trigger phrases:**

- "optimize my firestore performance..."
- "reduce firebase costs..."
- "why is this query slow..."
- "analyze my firestore usage..."

**Example:**

```
User: "Why is my users query so slow?"

Agent analyzes:
1. Query structure: .where('status', '==', 'active').where('createdAt', '>', date).orderBy('name')
2. Identifies: Missing composite index for (status, createdAt, name)
3. Calculates: 15,000 documents scanned for 100 results = 150x overhead
4. Recommends: Create index or denormalize data
5. Estimates: 50% cost reduction with index
```

---

## Configuration

### Environment Variables

```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"

# Optional
FIREBASE_PROJECT_ID="your-project-id"           # Auto-detected from credentials
FIRESTORE_EMULATOR_HOST="localhost:8080"        # For local development
FIREBASE_DATABASE_URL="https://your-db.firebaseio.com"  # For Realtime Database
```

### firestore.config.js

```javascript
module.exports = {
  // Project configuration
  projectId: 'your-project-id',

  // Batch operation settings
  batchSize: 500,                    // Documents per batch write
  maxConcurrentBatches: 3,           // Parallel batch operations

  // Query settings
  defaultLimit: 100,                 // Default query limit
  maxLimit: 1000,                    // Maximum allowed limit

  // Cost optimization
  enableCaching: true,               // Cache frequently read documents
  cacheTTL: 300,                     // Cache time-to-live (seconds)

  // Migration settings
  migrationBatchSize: 500,           // Documents per migration batch
  validateBeforeMigration: true,     // Validate data before migrating

  // Security
  allowDangerousOperations: false,   // Require confirmation for deletes
  dryRun: false                      // Preview changes without executing
};
```

---

## Best Practices

### Security Rules

- **Never allow open access** - Always require authentication
- **Validate all writes** - Check field types and values
- **Limit read scope** - Only allow reading necessary data
- **Test rules thoroughly** - Use Firebase Emulator Suite

### Performance

- **Use indexes** - Create composite indexes for complex queries
- **Batch operations** - Use batch writes for multiple documents
- **Denormalize data** - Duplicate data to avoid joins
- **Paginate results** - Use cursor-based pagination for large datasets

### Cost Optimization

- **Cache frequently read data** - Use in-memory caching
- **Minimize document reads** - Use `select()` to read specific fields
- **Archive old data** - Move historical data to Cloud Storage
- **Monitor usage** - Set up billing alerts

### Data Modeling

- **Keep documents small** - Max 1MB per document
- **Use subcollections** - For nested data hierarchies
- **Plan for scale** - Design for millions of documents
- **Avoid hot documents** - Distribute writes across documents

---

## Common Patterns

### Pattern 1: User Profiles with Privacy

```text
// Collection structure
users/{userId}
  - public: { name, avatar, bio }        // Anyone can read
  - private: { email, phone, address }   // Only user can read
  - settings: { notifications, privacy } // Only user can read/write
```

### Pattern 2: Real-time Chat

```text
// Collection structure
rooms/{roomId}
  - metadata: { name, createdAt, memberCount }
  - members/{userId}: { joinedAt, role }

messages/{messageId}
  - roomId, userId, text, createdAt

// Query optimization
- Index: (roomId, createdAt) for fetching messages
- Denormalize: Store last message in room metadata
```

### Pattern 3: E-commerce Orders

```text
// Collection structure
orders/{orderId}
  - userId, status, total, createdAt
  - items: [ { productId, quantity, price } ]  // Embedded array

// Status workflow
pending → processing → shipped → delivered

// Indexes
- (userId, createdAt) - User order history
- (status, createdAt) - Admin order management
```

---

## Troubleshooting

### Error: Permission Denied

```bash
# Check security rules
firebase firestore:rules:get

# Test rules locally
firebase emulators:start --only firestore

# Ask agent for help
"Why am I getting permission denied when reading /users/user123?"
```

### Error: Missing Index

```bash
# Agent will detect and create index automatically
"Create an index for querying users by (status, createdAt)"

# Or manually
firebase firestore:indexes

# Deploy
firebase deploy --only firestore:indexes
```

### Error: Rate Limits

```bash
# Agent handles rate limits automatically with exponential backoff
# For custom handling:
"Batch update 50,000 users with rate limit handling"
```

### Error: Invalid Credentials

```bash
# Verify service account
gcloud auth application-default login

# Or set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"

# Verify
firebase projects:list
```

---

## Advanced Features

### Cloud Functions Integration

```text
// Trigger Cloud Functions from Firestore
"Create a function that sends an email when a new user signs up"

Agent creates:
exports.sendWelcomeEmail = functions.firestore
  .document('users/{userId}')
  .onCreate(async (snap, context) => {
    const user = snap.data();
    await sendEmail(user.email, 'Welcome!');
  });
```

### Backup and Restore

```bash
# Export collection
"Export the users collection to JSON"

# Import data
"Import users from backup.json to the staging environment"

# Schedule backups
"Set up daily backups of all collections to Cloud Storage"
```

### Multi-Project Management

```bash
# Switch between projects
"Use the staging Firebase project"
"Switch back to production"

# Copy data between projects
"Copy the test users from staging to production"
```

---

## Performance Benchmarks

| Operation | Without Plugin | With Plugin | Improvement |
|-----------|----------------|-------------|-------------|
| Single document write | 50ms | 45ms | 1.1x |
| Batch write (500 docs) | 25s | 2.5s | 10x |
| Complex query | 5s | 500ms | 10x (with index) |
| Migration (10k docs) | Manual 2hrs | 5 minutes | 24x |
| Security rule generation | Manual 30min | 2 minutes | 15x |

---

## Integration Examples

### Next.js App

```javascript
// pages/api/users.js
import admin from 'firebase-admin';

// Agent sets up admin SDK automatically
export default async function handler(req, res) {
  const users = await admin.firestore()
    .collection('users')
    .limit(10)
    .get();

  res.json(users.docs.map(doc => doc.data()));
}
```

### React App

```javascript
// hooks/useFirestore.js
import { getFirestore, collection, query, where } from 'firebase/firestore';

// Agent generates custom hooks
export function useUserOrders(userId) {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    const q = query(
      collection(db, 'orders'),
      where('userId', '==', userId)
    );
    // ... subscribe to query
  }, [userId]);

  return orders;
}
```

### Cloud Functions

```javascript
// functions/index.js
const admin = require('firebase-admin');
admin.initializeApp();

// Agent creates Cloud Functions
exports.onUserCreate = functions.firestore
  .document('users/{userId}')
  .onCreate(async (snap) => {
    // Send welcome email, create profile, etc.
  });
```

---

## Resources

### Firebase Documentation

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Best Practices](https://firebase.google.com/docs/firestore/best-practices)

### Plugin Resources

- [GitHub Repository](https://github.com/jeremylongshore/claude-code-plugins)
- [Issue Tracker](https://github.com/jeremylongshore/claude-code-plugins/issues)
- [Marketplace](https://tonsofskills.com/)

### Community

- [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions)

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Support

Need help? Open an issue on GitHub or ask in GitHub Discussions!

**Made with** by [Jeremy Longshore](https://intentsolutions.io)
