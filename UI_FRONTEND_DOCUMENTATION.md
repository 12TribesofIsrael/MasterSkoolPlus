# 🎨 Skool Content Extractor V5.1 - Frontend UI Documentation

**Complete guide for implementing the modern web interface for Skool Content Extractor V5.1**

---

## 📋 Table of Contents

1. [🎯 UI Overview](#-ui-overview)
2. [🎨 Design System](#-design-system)
3. [🧩 Component Architecture](#-component-architecture)
4. [🔌 API Integration](#-api-integration)
5. [📱 Responsive Design](#-responsive-design)
6. [🎭 User Experience Flows](#-user-experience-flows)
7. [🧹 Cleanup System UI](#-cleanup-system-ui)
8. [🎥 Video Extraction UI](#-video-extraction-ui)
9. [📊 Analytics Dashboard](#-analytics-dashboard)
10. [🔧 Implementation Guide](#-implementation-guide)

---

## 🎯 UI Overview

### **Project Goals**
Create a modern, intuitive web interface that showcases the V5.1 capabilities:
- **95%+ video extraction success rate**
- **Comprehensive cleanup system** 
- **Production-ready reliability**
- **Enterprise-grade features**

### **Target Users**
- **Educators** extracting course content
- **Students** organizing learning materials  
- **Content Creators** backing up educational content
- **Enterprise Teams** managing bulk extractions

### **Core Value Propositions**
- ✅ **One-Click Extraction** - Simple URL input to complete download
- ✅ **Conflict-Free Operation** - Cleanup system prevents issues
- ✅ **Professional Results** - 95%+ success rate with clean organization
- ✅ **Enterprise Safety** - Automatic backups and restore capabilities

---

## 🎨 Design System

### **Visual Identity**

#### **Color Palette**
```css
/* Primary Colors */
--primary-blue: #2563eb;      /* Main brand color */
--primary-dark: #1d4ed8;      /* Dark variant */
--primary-light: #3b82f6;     /* Light variant */

/* Success & Status Colors */
--success-green: #10b981;     /* Success states */
--warning-amber: #f59e0b;     /* Warnings & cleanup */
--error-red: #ef4444;         /* Errors & failures */
--info-cyan: #06b6d4;         /* Information */

/* Cleanup System Colors */
--cleanup-orange: #f97316;    /* Cleanup actions */
--backup-blue: #0ea5e9;       /* Backup operations */
--restore-purple: #8b5cf6;    /* Restore functions */

/* Video Extraction Colors */
--video-success: #22c55e;     /* Successful extractions */
--platform-youtube: #ff0000;  /* YouTube red */
--platform-vimeo: #1ab7ea;    /* Vimeo blue */
--platform-loom: #625df5;     /* Loom purple */

/* Neutral Colors */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;
```

#### **Typography**
```css
/* Font Stack */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### **Spacing System**
```css
/* Spacing Scale (Tailwind-inspired) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### **Component Styling**

#### **Buttons**
```css
/* Primary Button */
.btn-primary {
  background: var(--primary-blue);
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: 0.5rem;
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Cleanup Button */
.btn-cleanup {
  background: var(--cleanup-orange);
  color: white;
}

/* Video Success Button */
.btn-video-success {
  background: var(--video-success);
  color: white;
}
```

#### **Cards**
```css
.card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: var(--space-6);
  border: 1px solid var(--gray-200);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-cleanup {
  border-left: 4px solid var(--cleanup-orange);
}

.card-video {
  border-left: 4px solid var(--video-success);
}
```

---

## 🧩 Component Architecture

### **Core Components Structure**
```
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   └── Footer.tsx
│   ├── cleanup/
│   │   ├── CleanupDashboard.tsx
│   │   ├── CommunityScanner.tsx
│   │   ├── CleanupStrategy.tsx
│   │   ├── BackupManager.tsx
│   │   └── StorageAnalytics.tsx
│   ├── extraction/
│   │   ├── URLInput.tsx
│   │   ├── JobManager.tsx
│   │   ├── ProgressTracker.tsx
│   │   └── ResultsDisplay.tsx
│   ├── video/
│   │   ├── VideoStatus.tsx
│   │   ├── PlatformBadges.tsx
│   │   ├── SuccessMetrics.tsx
│   │   └── VideoResults.tsx
│   ├── analytics/
│   │   ├── MetricCards.tsx
│   │   ├── SuccessChart.tsx
│   │   └── PerformanceDashboard.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── Modal.tsx
│       ├── Toast.tsx
│       └── ProgressBar.tsx
├── hooks/
│   ├── useCleanup.ts
│   ├── useExtraction.ts
│   ├── useVideoStatus.ts
│   └── useAnalytics.ts
├── services/
│   ├── api.ts
│   ├── cleanup.ts
│   ├── extraction.ts
│   └── websocket.ts
└── types/
    ├── cleanup.ts
    ├── extraction.ts
    └── video.ts
```

### **Key Component Specifications**

#### **1. CleanupDashboard Component**
```tsx
interface CleanupDashboardProps {
  onCleanupComplete: (result: CleanupResult) => void;
  showPreExtraction?: boolean;
}

// Features:
// - Community scanning and display
// - Cleanup strategy selection
// - Storage analytics visualization
// - Backup management interface
// - Real-time progress tracking
```

#### **2. VideoStatus Component**
```tsx
interface VideoStatusProps {
  jobId: string;
  onStatusUpdate: (status: VideoExtractionStatus) => void;
}

// Features:
// - Platform detection badges
// - Real-time success rate counter
// - Safe extraction method indicator
// - Platform-specific progress bars
// - Failed extraction reporting
```

#### **3. URLInput Component**
```tsx
interface URLInputProps {
  onSubmit: (url: string, options: ExtractionOptions) => void;
  onValidation: (isValid: boolean, communityInfo?: CommunityInfo) => void;
}

// Features:
// - Real-time URL validation
// - Community preview display
// - Conflict warning system
// - Job type selection (single/collection)
// - Advanced options panel
```

---

## 🔌 API Integration

### **API Service Architecture**

#### **Base API Service**
```typescript
class APIService {
  private baseURL: string;
  private wsConnection?: WebSocket;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  // HTTP Methods
  async get<T>(endpoint: string): Promise<T> { }
  async post<T>(endpoint: string, data: any): Promise<T> { }
  async put<T>(endpoint: string, data: any): Promise<T> { }
  async delete<T>(endpoint: string): Promise<T> { }

  // WebSocket Methods
  connectWebSocket(jobId: string, onMessage: (data: any) => void) { }
  disconnectWebSocket() { }
}
```

### **MVP Backend Integration Contract**

This UI depends on a minimal HTTP/WS adapter wrapping the Python extractors. Implement these endpoints to enable the MVP end-to-end.

#### 1) Start Extraction
- POST `/api/extract/start`
- Body:
```json
{ "url": "string", "mode": "single"|"collection", "options": { "downloadVideos": false, "preCleanup": false } }
```
- Returns: `{ "jobId": "string" }`

#### 2) Job Status (poll)
- GET `/api/jobs/{jobId}/status`
- Returns:
```json
{ "phase": "auth"|"cleanup"|"scan"|"video"|"content"|"finalizing"|"done"|"error", "progress": 0, "message": "string" }
```

#### 3) Video Status (poll or WS)
- GET `/api/extract/video-status/{jobId}`
- Returns:
```json
{
  "successRate": 0,
  "totalVideos": 0,
  "extractedUrls": 0,
  "failedExtractions": 0,
  "platformsDetected": [ { "name": "YouTube", "detected": 0, "extracted": 0, "failed": 0, "status": "pending" } ],
  "usingSafeMethod": true,
  "duplicateWatch": { "suspected": 0, "blocked": 0, "knownIds": [] }
}
```
- WS `/ws/jobs/{jobId}` and `/ws/video/{jobId}` stream the same payloads. UI will poll every 2s if WS is unavailable.

#### 4) Results
- GET `/api/results/{jobId}`
- Returns:
```json
{
  "community": "string",
  "lessons": 0,
  "videoExtractionRate": 0,
  "platformBreakdown": [ { "name": "YouTube", "detected": 0, "extracted": 0, "failed": 0, "status": "completed" } ],
  "storageUsed": 0,
  "outputPaths": { "communityDir": "string", "lessonsDir": "string", "imagesDir": "string", "videosDir": "string" },
  "duplicates": { "hasDuplicates": false, "urls": [], "lessonFiles": [] }
}
```

#### 5) Cleanup
- POST `/api/cleanup/scan` → `{ existingCommunities, totalSize, totalFiles }`
- POST `/api/cleanup/execute` `{ strategy }` → `{ cleaned, backupId }`
- GET `/api/cleanup/backups` → `BackupInfo[]`
- POST `/api/cleanup/restore` `{ backupId }` → `{ restored: boolean }`

#### UI Requirements
- Display "Duplicate Video Watch" using `duplicateWatch` fields.
- Progress timeline uses `phase` values.
- Poll if WS not available.
- Show duplicate banner if `duplicates.hasDuplicates` is true with link to details.

#### **Cleanup API Service**
```typescript
class CleanupService extends APIService {
  async scanCommunities(): Promise<CleanupStatus> {
    return this.get<CleanupStatus>('/api/cleanup/scan');
  }

  async executeCleanup(strategy: CleanupStrategy): Promise<CleanupResult> {
    return this.post<CleanupResult>('/api/cleanup/execute', strategy);
  }

  async listBackups(): Promise<BackupInfo[]> {
    return this.get<BackupInfo[]>('/api/cleanup/backups');
  }

  async restoreBackup(backupId: string): Promise<RestoreResult> {
    return this.post<RestoreResult>('/api/cleanup/restore', { backupId });
  }

  async getStorageAnalytics(): Promise<StorageAnalytics> {
    return this.get<StorageAnalytics>('/api/storage/analytics');
  }
}
```

#### **Extraction API Service**
```typescript
class ExtractionService extends APIService {
  async startExtraction(request: ExtractionRequest): Promise<ExtractionJob> {
    return this.post<ExtractionJob>('/api/extract/start', request);
  }

  async getJobStatus(jobId: string): Promise<JobStatus> {
    return this.get<JobStatus>(`/api/jobs/${jobId}/status`);
  }

  async getVideoStatus(jobId: string): Promise<VideoExtractionStatus> {
    return this.get<VideoExtractionStatus>(`/api/extract/video-status/${jobId}`);
  }

  async getResults(jobId: string): Promise<ExtractionResults> {
    return this.get<ExtractionResults>(`/api/results/${jobId}`);
  }

  async cancelJob(jobId: string): Promise<void> {
    return this.delete(`/api/jobs/${jobId}`);
  }
}
```

### **Real-Time Updates**

#### **WebSocket Integration**
```typescript
// Real-time job progress updates
const useJobProgress = (jobId: string) => {
  const [progress, setProgress] = useState<JobProgress | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080/ws/jobs/${jobId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);
    };

    return () => ws.close();
  }, [jobId]);

  return progress;
};

// Real-time video extraction status
const useVideoProgress = (jobId: string) => {
  const [videoStatus, setVideoStatus] = useState<VideoExtractionStatus | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080/ws/video/${jobId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setVideoStatus(data);
    };

    return () => ws.close();
  }, [jobId]);

  return videoStatus;
};
```

---

## 📱 Responsive Design

### **Breakpoint System**
```css
/* Mobile First Approach */
/* xs: 0px - 475px */
/* sm: 476px - 640px */
/* md: 641px - 768px */
/* lg: 769px - 1024px */
/* xl: 1025px - 1280px */
/* 2xl: 1281px+ */

@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### **Responsive Layout Examples**

#### **Main Dashboard Layout**
```tsx
// Desktop Layout
<div className="grid grid-cols-12 gap-6">
  <div className="col-span-8">
    <URLInput />
    <ProgressTracker />
  </div>
  <div className="col-span-4">
    <CleanupPanel />
    <VideoStatus />
  </div>
</div>

// Mobile Layout  
<div className="space-y-4">
  <URLInput />
  <div className="grid grid-cols-2 gap-4">
    <CleanupPanel />
    <VideoStatus />
  </div>
  <ProgressTracker />
</div>
```

#### **Cleanup Dashboard Responsive**
```tsx
// Desktop: 3-column grid
<div className="grid grid-cols-3 gap-6">
  <CommunityList />
  <CleanupOptions />
  <BackupManager />
</div>

// Tablet: 2-column grid
<div className="grid grid-cols-2 gap-4">
  <div className="col-span-2"><CommunityList /></div>
  <CleanupOptions />
  <BackupManager />
</div>

// Mobile: Single column
<div className="space-y-4">
  <CommunityList />
  <CleanupOptions />
  <BackupManager />
</div>
```

---

## 🎭 User Experience Flows

### **Primary User Flow: Complete Extraction**

#### **Step 1: Landing & Setup**
```
┌─────────────────────────────────────┐
│ 🎯 Welcome to Skool Extractor V5.1 │
│                                     │
│ ✅ 95%+ Video Success Rate         │
│ 🧹 Cleanup System Included         │
│ 🛡️ Automatic Backups              │
│                                     │
│ [Get Started] [Learn More]         │
└─────────────────────────────────────┘
```

#### **Step 2: URL Input & Validation**
```
┌─────────────────────────────────────┐
│ Enter Skool Community URL           │
│                                     │
│ [https://skool.com/community/...  ] │
│ ✅ Valid URL - AI Money Lab found   │
│                                     │
│ 📊 Estimated: 26 lessons, ~45 min  │
│ 🎥 Video platforms: YouTube, Vimeo  │
│                                     │
│ ○ Single Lesson  ● Full Community  │
│ [Start Extraction]                  │
└─────────────────────────────────────┘
```

#### **Step 3: Pre-Extraction Cleanup Check**
```
┌─────────────────────────────────────┐
│ 🧹 Cleanup Check                   │
│                                     │
│ Found existing community:           │
│ • AI Money Lab (45MB, 23 files)    │
│                                     │
│ ⚠️ This may cause conflicts        │
│                                     │
│ [Clean First] [Continue] [Cancel]  │
└─────────────────────────────────────┘
```

#### **Step 4: Extraction Progress**
```
┌─────────────────────────────────────┐
│ 🚀 Extracting: AI Money Lab        │
│                                     │
│ ████████████░░░░ 75% Complete       │
│ Processing lesson 19 of 26          │
│                                     │
│ 🎥 Video Extraction: 18/19 (94.7%) │
│ ✅ YouTube: 15/15  ✅ Vimeo: 3/4   │
│                                     │
│ 🔍 Current: "Advanced SEO Tactics" │
│ ⏱️ ETA: 8 minutes remaining        │
│                                     │
│ [Cancel Extraction]                 │
└─────────────────────────────────────┘
```

#### **Step 5: Results & Download**
```
┌─────────────────────────────────────┐
│ 🎉 Extraction Complete!            │
│                                     │
│ 📊 Results Summary:                 │
│ • 26 lessons extracted             │
│ • 96.2% video success rate         │
│ • 45 images downloaded             │
│ • 156MB total size                 │
│                                     │
│ 🎥 Video Breakdown:                 │
│ • YouTube: 20/20 ✅               │
│ • Vimeo: 5/5 ✅                   │
│ • Loom: 1/1 ✅                    │
│                                     │
│ [Download All] [View Files]        │
│ [Download Videos Only]              │
└─────────────────────────────────────┘
```

### **Cleanup System Flow**

#### **Cleanup Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│ 🧹 Cleanup Management Dashboard                            │
│                                                             │
│ 📊 Storage Overview:                                        │
│ ████████░░ 125MB used of 1GB (12.5%)                      │
│                                                             │
│ 📁 Existing Communities (3):                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✅ AI Money Lab        45MB  23 files  Aug 15, 2024   │ │
│ │ ✅ New Society         12MB   8 files  Aug 14, 2024   │ │
│ │ ✅ AI Automation       67MB  45 files  Aug 10, 2024   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ 🎯 Cleanup Options:                                         │
│ [Clean All] [Select Specific] [By Date] [By Size]         │
│                                                             │
│ 💾 Recent Backups (2):                                     │
│ • backup_20240815_143022.zip (89MB)                       │
│ • backup_20240814_091533.zip (72MB)                       │
│                                                             │
│ [View All Backups] [Create Manual Backup]                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧹 Cleanup System UI

### **Community Scanner Component**
```tsx
interface CommunityScannerProps {
  onScanComplete: (communities: Community[]) => void;
  autoScan?: boolean;
}

const CommunityScanner: React.FC<CommunityScannerProps> = ({
  onScanComplete,
  autoScan = true
}) => {
  const [scanning, setScanning] = useState(false);
  const [communities, setCommunities] = useState<Community[]>([]);

  return (
    <Card className="card-cleanup">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">📁 Community Scanner</h3>
        {scanning && <Spinner size="sm" />}
      </div>
      
      {communities.length > 0 ? (
        <div className="space-y-3">
          {communities.map(community => (
            <div key={community.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium">{community.name}</h4>
                <p className="text-sm text-gray-600">
                  {formatBytes(community.size)} • {community.fileCount} files • {formatDate(community.lastModified)}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                {community.hasVideos && <Badge variant="video">Videos</Badge>}
                {community.hasImages && <Badge variant="images">Images</Badge>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <FolderIcon className="h-12 w-12 mx-auto mb-2" />
          <p>No communities found</p>
        </div>
      )}
    </Card>
  );
};
```

### **Cleanup Strategy Selector**
```tsx
const CleanupStrategy: React.FC = () => {
  const [selectedStrategy, setSelectedStrategy] = useState<'all' | 'selective' | 'date' | 'size'>('selective');

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-4">🎯 Cleanup Strategy</h3>
      
      <div className="space-y-3">
        <RadioOption
          value="all"
          selected={selectedStrategy === 'all'}
          onChange={setSelectedStrategy}
          icon="🗑️"
          title="Clean All Communities"
          description="Remove all existing communities (with backup)"
        />
        
        <RadioOption
          value="selective" 
          selected={selectedStrategy === 'selective'}
          onChange={setSelectedStrategy}
          icon="🎯"
          title="Selective Cleanup"
          description="Choose specific communities to remove"
        />
        
        <RadioOption
          value="date"
          selected={selectedStrategy === 'date'}
          onChange={setSelectedStrategy}
          icon="📅"
          title="Date-Based Cleanup"
          description="Remove communities older than X days"
        />
        
        <RadioOption
          value="size"
          selected={selectedStrategy === 'size'}
          onChange={setSelectedStrategy}
          icon="📊"
          title="Size-Based Cleanup"
          description="Target largest communities first"
        />
      </div>
      
      <Button 
        className="w-full mt-4 btn-cleanup"
        onClick={handleCleanup}
      >
        Start Cleanup
      </Button>
    </Card>
  );
};
```

### **Backup Manager Component**
```tsx
const BackupManager: React.FC = () => {
  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [showRestoreModal, setShowRestoreModal] = useState(false);

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">💾 Backup Manager</h3>
        <Button size="sm" onClick={createManualBackup}>
          Create Backup
        </Button>
      </div>
      
      <div className="space-y-2">
        {backups.map(backup => (
          <div key={backup.id} className="flex items-center justify-between p-2 bg-blue-50 rounded">
            <div>
              <p className="font-medium text-sm">{backup.name}</p>
              <p className="text-xs text-gray-600">
                {formatBytes(backup.size)} • {formatDate(backup.createdAt)}
              </p>
            </div>
            <div className="flex space-x-2">
              <Button size="xs" variant="outline" onClick={() => downloadBackup(backup.id)}>
                Download
              </Button>
              <Button size="xs" onClick={() => restoreBackup(backup.id)}>
                Restore
              </Button>
            </div>
          </div>
        ))}
      </div>
      
      {backups.length === 0 && (
        <div className="text-center py-4 text-gray-500">
          <p className="text-sm">No backups available</p>
        </div>
      )}
    </Card>
  );
};
```

---

## 🎥 Video Extraction UI

### **Platform Status Badges**
```tsx
const PlatformBadges: React.FC<{ platforms: Platform[] }> = ({ platforms }) => {
  return (
    <div className="flex flex-wrap gap-2">
      {platforms.map(platform => (
        <Badge 
          key={platform.name}
          variant={platform.status}
          className={`platform-${platform.name.toLowerCase()}`}
        >
          <div className="flex items-center space-x-2">
            <PlatformIcon name={platform.name} />
            <span>{platform.name}</span>
            <span className="text-xs">
              {platform.extracted}/{platform.detected}
            </span>
            {platform.status === 'completed' && (
              <CheckIcon className="h-3 w-3" />
            )}
          </div>
        </Badge>
      ))}
    </div>
  );
};
```

### **Video Success Metrics**
```tsx
const VideoSuccessMetrics: React.FC<{ status: VideoExtractionStatus }> = ({ status }) => {
  return (
    <Card className="card-video">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">🎥 Video Extraction</h3>
        {status.usingSafeMethod && (
          <Badge variant="success">Safe Method Active</Badge>
        )}
      </div>
      
      <div className="space-y-4">
        <div className="text-center">
          <div className="text-3xl font-bold text-video-success">
            {status.successRate.toFixed(1)}%
          </div>
          <p className="text-sm text-gray-600">Success Rate</p>
        </div>
        
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xl font-semibold">{status.totalVideos}</div>
            <p className="text-xs text-gray-600">Total Videos</p>
          </div>
          <div>
            <div className="text-xl font-semibold text-green-600">{status.extractedUrls}</div>
            <p className="text-xs text-gray-600">Extracted</p>
          </div>
          <div>
            <div className="text-xl font-semibold text-red-600">{status.failedExtractions}</div>
            <p className="text-xs text-gray-600">Failed</p>
          </div>
        </div>
        
        <PlatformBadges platforms={status.platformsDetected} />
        
        {status.currentPlatform && (
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm">
              <span className="font-medium">Currently processing:</span> {status.currentPlatform}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};
```

---

## 📊 Analytics Dashboard

### **Success Metrics Cards**
```tsx
const MetricCards: React.FC<{ metrics: PerformanceMetrics }> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Overall Success Rate"
        value={`${metrics.overallSuccessRate}%`}
        change="+2.3%"
        trend="up"
        icon="🎯"
        color="success"
      />
      
      <MetricCard
        title="Video Extraction"
        value={`${metrics.videoSuccessRate}%`}
        change="+5.1%"
        trend="up"
        icon="🎥"
        color="video"
      />
      
      <MetricCard
        title="Communities Processed"
        value={metrics.totalCommunities}
        change="+12"
        trend="up"
        icon="📁"
        color="info"
      />
      
      <MetricCard
        title="Storage Optimized"
        value={formatBytes(metrics.storageOptimized)}
        change="-2.1GB"
        trend="down"
        icon="🧹"
        color="cleanup"
      />
    </div>
  );
};
```

### **Success Rate Chart**
```tsx
const SuccessRateChart: React.FC = () => {
  const data = [
    { platform: 'YouTube', rate: 96.1, color: '#ff0000' },
    { platform: 'Vimeo', rate: 93.4, color: '#1ab7ea' },
    { platform: 'Loom', rate: 92.7, color: '#625df5' },
    { platform: 'Wistia', rate: 89.8, color: '#54a3ff' },
    { platform: 'Direct', rate: 98.2, color: '#22c55e' }
  ];

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-4">📊 Platform Success Rates</h3>
      <div className="space-y-4">
        {data.map(item => (
          <div key={item.platform} className="space-y-2">
            <div className="flex justify-between">
              <span className="font-medium">{item.platform}</span>
              <span className="font-semibold">{item.rate}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="h-2 rounded-full transition-all duration-500"
                style={{ 
                  width: `${item.rate}%`,
                  backgroundColor: item.color 
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
```

---

## 🔧 Implementation Guide

### **Getting Started**

#### **1. Project Setup**
```bash
# Create new React project with TypeScript
npx create-react-app skool-extractor-ui --template typescript

# Install dependencies
npm install @tanstack/react-query zustand framer-motion
npm install @headlessui/react @heroicons/react
npm install tailwindcss @tailwindcss/forms
npm install recharts date-fns
```

#### **2. Tailwind Configuration**
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8'
        },
        cleanup: {
          500: '#f97316',
          600: '#ea580c'
        },
        video: {
          success: '#22c55e'
        }
      }
    }
  },
  plugins: [require('@tailwindcss/forms')]
}
```

#### **3. State Management Setup**
```typescript
// stores/useAppStore.ts
import { create } from 'zustand';

interface AppState {
  // Cleanup State
  cleanupStatus: CleanupStatus | null;
  setCleanupStatus: (status: CleanupStatus) => void;
  
  // Extraction State
  currentJob: ExtractionJob | null;
  setCurrentJob: (job: ExtractionJob | null) => void;
  
  // Video Status
  videoStatus: VideoExtractionStatus | null;
  setVideoStatus: (status: VideoExtractionStatus) => void;
  
  // UI State
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  cleanupStatus: null,
  setCleanupStatus: (status) => set({ cleanupStatus: status }),
  
  currentJob: null,
  setCurrentJob: (job) => set({ currentJob: job }),
  
  videoStatus: null,
  setVideoStatus: (status) => set({ videoStatus: status }),
  
  theme: 'light',
  toggleTheme: () => set((state) => ({ 
    theme: state.theme === 'light' ? 'dark' : 'light' 
  }))
}));
```

### **Key Implementation Patterns**

#### **Real-Time Updates with React Query**
```typescript
// hooks/useJobProgress.ts
import { useQuery } from '@tanstack/react-query';

export const useJobProgress = (jobId: string | null) => {
  return useQuery({
    queryKey: ['job-progress', jobId],
    queryFn: () => jobId ? api.getJobStatus(jobId) : null,
    enabled: !!jobId,
    refetchInterval: 2000, // Poll every 2 seconds
    refetchIntervalInBackground: true
  });
};
```

#### **Optimistic Updates for Cleanup**
```typescript
// hooks/useCleanup.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useCleanup = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (strategy: CleanupStrategy) => api.executeCleanup(strategy),
    onMutate: async (strategy) => {
      // Optimistically update UI
      await queryClient.cancelQueries(['communities']);
      const previousCommunities = queryClient.getQueryData(['communities']);
      
      // Show cleaning state immediately
      queryClient.setQueryData(['communities'], []);
      
      return { previousCommunities };
    },
    onError: (err, strategy, context) => {
      // Rollback on error
      if (context?.previousCommunities) {
        queryClient.setQueryData(['communities'], context.previousCommunities);
      }
    },
    onSettled: () => {
      // Refetch to get actual state
      queryClient.invalidateQueries(['communities']);
    }
  });
};
```

This comprehensive UI documentation provides everything needed to implement the modern web interface for the Skool Content Extractor V5.1, showcasing both the cleanup system and advanced video extraction capabilities in a professional, user-friendly interface.