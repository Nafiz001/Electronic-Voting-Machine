# Voting Website - Firebase Integration

This voting website now connects to your Firebase Realtime Database and displays real-time voting data.

## Firebase Database Structure

Your database should have this structure:
```
https://e-vm-f7bdf-default-rtdb.firebaseio.com/
├── voters/
│   ├── 5/
│   │   └── name: "NAFIZ"
│   ├── 6/
│   │   └── name: "AUVRO"
│   └── ...
└── votes/
    ├── -ObMq8EjjWSm21ejPt2N/
    │   ├── candidate: "Charlie"
    │   ├── timestamp: "2025-10-12T09:55:18.560103"
    │   └── voter_id: "10"
    ├── -ObMwIyevpQ7hEZVPZcj/
    │   ├── candidate: "Alice"
    │   ├── timestamp: "2025-10-12T10:22:15.379101"
    │   └── voter_id: "5"
    └── ...
```

## Candidates

The system supports three candidates:
- **Alice** - Progressive Party (🌟)
- **Bob** - Unity Party (🏛️)
- **Charlie** - Reform Party (🚀)

## Features

### 1. Dashboard
- Real-time statistics from Firebase
- Total voters count
- Total votes cast
- Current turnout rate
- Auto-refresh every 30 seconds

### 2. Voter List
- Shows all registered voters from Firebase
- Displays voting status (voted/not voted)
- Shows which candidate they voted for
- Real-time updates every 30 seconds

### 3. Vote Count
- Live vote counting for Alice, Bob, and Charlie
- Real-time percentage calculations
- Leading candidate display
- Auto-refresh every 15 seconds for live updates

### 4. Vote Statistics
- Visual charts showing vote distribution
- Real-time data from Firebase
- Interactive charts using Recharts library

### 5. Candidates Page
- Updated to show Alice, Bob, and Charlie
- Party information and platforms

## How It Works

The application uses Firebase REST API to:
1. Fetch voter data from `/voters.json`
2. Fetch vote data from `/votes.json`
3. Calculate statistics and voting status
4. Display real-time results

## Firebase Service

The `firebase.js` service provides these methods:
- `getVoters()` - Get all registered voters
- `getVotes()` - Get all cast votes
- `getVotersWithStatus()` - Get voters with their voting status
- `getVoteCounts()` - Get vote counts per candidate
- `getDashboardStats()` - Get overall statistics

## Running the Application

1. Make sure your Firebase database is accessible
2. Start the development server:
   ```bash
   npm run dev
   ```
3. Open http://localhost:5173 in your browser
4. The app will automatically fetch data from Firebase

## Auto-Refresh

The application automatically refreshes data:
- Dashboard: Every 30 seconds
- Voter List: Every 30 seconds  
- Vote Count: Every 15 seconds (for live updates)
- Vote Statistics: Every 30 seconds

You can also manually refresh using the "Refresh" button on each page.

## Error Handling

If Firebase is unreachable or returns errors:
- The app will show loading states
- Error messages are logged to console
- Default values are displayed
- Users can manually retry with refresh buttons