# 🗳️ Voting Machine Website

A modern, aesthetically designed React-based voting system web application with comprehensive features for managing elections, tracking votes, and analyzing results.

## ✨ Features

- **📊 Dashboard**: Overview of voting system statistics with real-time metrics
- **👥 Voter List**: Complete voter management with search and filtering capabilities
- **🎯 Candidates**: Detailed candidate profiles with party information and agendas
- **🗳️ Vote Count**: Real-time vote tracking and results display
- **📈 Vote Statistics**: Comprehensive analytics with interactive charts and graphs

## 🎨 Design

- Modern, clean UI with a professional purple gradient color scheme
- Responsive design that works on all devices
- Smooth animations and transitions
- Intuitive navigation with emoji icons
- Beautiful data visualizations using Recharts

## 🚀 Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

## 📦 Technologies Used

- **React** - Frontend framework
- **React Router** - Navigation and routing
- **Recharts** - Data visualization
- **Vite** - Build tool and dev server
- **CSS3** - Styling with modern features

## 🎯 Project Structure

```
src/
├── components/
│   ├── Navigation.jsx      # Sidebar navigation component
│   └── Navigation.css
├── pages/
│   ├── Dashboard.jsx        # Main dashboard page
│   ├── VoterList.jsx        # Voter management page
│   ├── Candidates.jsx       # Candidates information page
│   ├── VoteCount.jsx        # Vote counting page
│   ├── VoteStatistics.jsx   # Statistics and analytics page
│   └── [corresponding CSS files]
├── App.jsx                  # Main app component with routing
├── App.css
├── main.jsx                 # Entry point
└── index.css                # Global styles
```

## � Firebase Integration

**NEW**: This application now connects to Firebase Realtime Database for live voting data!

### Current Setup
- **Firebase URL**: `https://e-vm-f7bdf-default-rtdb.firebaseio.com/`
- **Candidates**: Alice, Bob, and Charlie
- **Real-time updates**: Auto-refresh every 15-30 seconds
- **Live vote counting**: Shows actual votes from your Firebase database

### Features
- ✅ Real-time vote counting from Firebase
- ✅ Live voter status tracking
- ✅ Auto-refreshing dashboards
- ✅ Firebase REST API integration
- ✅ Error handling and loading states
- ✅ Manual refresh buttons

### Database Structure
```json
{
  "voters": {
    "5": { "name": "NAFIZ" },
    "6": { "name": "AUVRO" }
  },
  "votes": {
    "-ObMq8EjjWSm21ejPt2N": {
      "candidate": "Charlie",
      "timestamp": "2025-10-12T09:55:18.560103",
      "voter_id": "10"
    }
  }
}
```

See `FIREBASE_INTEGRATION.md` for detailed documentation.

## 🎨 Color Palette

- Primary Purple: `#667eea` → `#764ba2`
- Success Green: `#48bb78`
- Warning Orange: `#ed8936`
- Error Red: `#f56565`
- Info Blue: `#3b82f6`
- Background: `#f7fafc`
- Text: `#2d3748`

## 📄 License

This project is created for educational and demonstration purposes.

## 🤝 Contributing

Feel free to fork this project and customize it for your voting machine needs!

---

Built with ❤️ using React and Vite

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
