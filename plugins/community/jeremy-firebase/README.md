# jeremy-firebase

**Production-ready Firebase platform operations plugin with Vertex AI Gemini integration.**

## Overview

Comprehensive automation for Firebase services including Authentication, Cloud Storage, Hosting, Cloud Functions, Analytics, and AI-powered features using Vertex AI Gemini.

## Features

### Core Firebase Services

- **Firebase Authentication** - User management, custom claims, OAuth providers
- **Cloud Firestore** - Document CRUD, queries, security rules, indexes
- **Cloud Storage** - File uploads, security rules, signed URLs
- **Firebase Hosting** - Static site deployment, custom domains, SSL
- **Cloud Functions** - TypeScript/JavaScript functions, HTTP/callable/scheduled triggers
- **Firebase Analytics** - Event logging, user properties, conversion tracking

### AI Integration (Vertex AI Gemini)

- **Embeddings Generation** - Text-to-vector for semantic search
- **Content Analysis** - Gemini API for content moderation, classification
- **Chat Integration** - Conversational AI with Firebase data context
- **Model Deployment** - Custom AI models with Firebase ML
- **RAG Implementation** - Retrieval-Augmented Generation with Firestore vector search

### DevOps & Operations

- **Firebase CLI Automation** - Project init, deployment, emulator control
- **Environment Management** - Multiple Firebase projects (dev, staging, prod)
- **Security Rules Testing** - Automated testing of Firestore and Storage rules
- **Performance Monitoring** - Integration with Firebase Performance Monitoring
- **Remote Config** - Feature flags and A/B testing setup

## Installation

```bash
/plugin install jeremy-firebase@claude-code-plugins-plus
```

## Prerequisites

- Firebase CLI: `npm install -g firebase-tools`
- Node.js 18+
- Google Cloud Project with Firebase enabled
- Vertex AI API enabled (for AI features)

## Quick Start

### Initialize Firebase Project

```bash
firebase login
firebase init
```

### Deploy to Firebase

Use the slash commands:

```bash
/firebase-deploy-hosting
/firebase-deploy-functions
/firebase-deploy-rules
```

### Environment Configuration

Create `.env.local`:

```bash
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
VERTEX_AI_LOCATION=us-central1
```

## Available Commands

The plugin provides slash commands for common Firebase operations:

- `/firebase-init-project` - Initialize new Firebase project
- `/firebase-deploy-hosting` - Deploy static site to Firebase Hosting
- `/firebase-deploy-functions` - Deploy Cloud Functions
- `/firebase-deploy-rules` - Deploy Firestore and Storage security rules
- `/firebase-auth-setup` - Configure Firebase Authentication providers
- `/firebase-vertex-ai-embeddings` - Generate embeddings with Vertex AI
- `/firebase-firestore-query` - Execute Firestore queries
- `/firebase-storage-upload` - Upload files to Cloud Storage

See `/firebase-help` for complete command list.

## Agent Skills

This plugin includes Agent Skills that automatically activate based on trigger phrases:

### firebase-vertex-ai

**Triggers:** "integrate vertex ai", "add gemini to firebase", "generate embeddings"

Automatically sets up Vertex AI Gemini integration with Firebase, including:

- Content moderation for user-generated content
- Semantic search with embeddings
- Conversational AI chatbots
- Image analysis with Gemini Vision

## Architecture

```
Firebase Project
├── Authentication (user management)
├── Firestore (NoSQL database)
├── Cloud Storage (file storage)
├── Cloud Functions (serverless backend)
├── Firebase Hosting (static site hosting)
└── Vertex AI Integration
    ├── Gemini 2.0 Flash (content analysis)
    ├── Text Embeddings (semantic search)
    └── Custom Models (ML deployment)
```

## Example Use Cases

### 1. User Registration with AI Content Moderation

```javascript
// Cloud Function triggered on user creation
exports.moderateUserProfile = functions.firestore
  .document('users/{userId}')
  .onCreate(async (snap, context) => {
    const {VertexAI} = require('@google-cloud/vertexai');
    const vertex = new VertexAI({project: 'PROJECT_ID', location: 'us-central1'});
    const model = vertex.getGenerativeModel({model: 'gemini-2.5-flash'});

    const userBio = snap.data().bio;
    const result = await model.generateContent(`Moderate this user bio for inappropriate content: ${userBio}`);

    if (result.response.text().includes('INAPPROPRIATE')) {
      await snap.ref.update({status: 'pending_review'});
    }
  });
```

### 2. Semantic Search with Firestore

```javascript
// Generate embeddings and store in Firestore
const embedding = await generateEmbedding(documentText);
await firestore.collection('documents').add({
  text: documentText,
  embedding: embedding,
  createdAt: admin.firestore.FieldValue.serverTimestamp()
});

// Query by similarity
const queryEmbedding = await generateEmbedding(searchQuery);
const results = await vectorSearch(queryEmbedding, 10);
```

### 3. AI-Powered Chatbot

```javascript
// Cloud Function for chat endpoint
exports.chat = functions.https.onCall(async (data, context) => {
  const {VertexAI} = require('@google-cloud/vertexai');
  const vertex = new VertexAI({project: 'PROJECT_ID'});
  const model = vertex.getGenerativeModel({model: 'gemini-2.5-flash'});

  // Get conversation history from Firestore
  const history = await getConversationHistory(context.auth.uid);

  const result = await model.generateContent({
    contents: [...history, {role: 'user', parts: [{text: data.message}]}]
  });

  return {reply: result.response.text()};
});
```

## Security Best Practices

### Firestore Security Rules

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function isAuthenticated() {
      return request.auth != null;
    }

    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }

    match /users/{userId} {
      allow read: if isOwner(userId);
      allow write: if isOwner(userId);
    }
  }
}
```

### Storage Security Rules

```text
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{userId}/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId
                   && request.resource.size < 10 * 1024 * 1024; // 10MB limit
    }
  }
}
```

## Performance Optimization

- **Batch Firestore Operations** - Use batch writes for multiple document updates
- **Firebase Functions Cold Starts** - Implement function warming strategies
- **Vertex AI Rate Limits** - Implement exponential backoff and retry logic
- **Storage Upload Optimization** - Use resumable uploads for large files
- **Hosting Cache Headers** - Configure proper caching in firebase.json

## Troubleshooting

### Common Issues

**Issue:** Firebase CLI not found

```bash
npm install -g firebase-tools
```

**Issue:** Authentication failed

```bash
firebase login --reauth
```

**Issue:** Vertex AI quota exceeded

- Check quotas in GCP Console
- Implement rate limiting in Cloud Functions
- Use caching to reduce API calls

**Issue:** Firestore permissions denied

- Check security rules in Firebase Console
- Verify user is authenticated
- Review IAM permissions

## Configuration

### firebase.json

```json
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": {
    "source": "functions"
  },
  "hosting": {
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
  },
  "storage": {
    "rules": "storage.rules"
  }
}
```

## Documentation

For detailed plugin documentation and Firebase integration guides, see:

- Plugin documentation: `000-usermanuals/`
- Firebase docs: https://firebase.google.com/docs
- Vertex AI docs: https://cloud.google.com/vertex-ai/docs

## License

MIT License - See LICENSE file

## Author

Jeremy Longshore

- GitHub: https://github.com/jeremylongshore
- Plugin Marketplace: https://tonsofskills.com

## Support

- Issues: https://github.com/jeremylongshore/claude-code-plugins/issues
- Discussions: https://github.com/jeremylongshore/claude-code-plugins/discussions

---

**Version:** 1.0.0
**Category:** Integration
**Plugin Type:** AI Instruction + Agent Skills
**Last Updated:** 2025-11-13
